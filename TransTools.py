import datetime
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QEvent, QThread, pyqtSignal
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtGui import QIcon
import qdarkstyle
from mainwindow import Ui_MainWindow
from TransBaseFunc import showmsg,auto_begin_task
from TransDataProvider import TransDataProvider, TransDataBase
from TransManual import TransManual
from TransSetting import TransSetting
from TransModels import TransModelInit


class Main(QtWidgets.QMainWindow, Ui_MainWindow):
    """主窗口"""
    def __init__(self):

        super(Main, self).__init__()  # 初始化
        self.setupUi(self)

        self._database = TransDataBase()  # 在此处写入基础数据
        self._provider = TransDataProvider()  # 数据提供对象

        self._manual = None   # 手动传输窗口
        self._setting = None  # 设置窗口

        self.transinfo_list = None  # 传输列表

        self.trayicon = QSystemTrayIcon(self)  # 系统托盘
        self.trayiconmenu = QMenu(self)
        self.icon = QIcon('logo.png')
        self.create_trayicon()

        self.tableView_log.verticalHeader().hide()  # 隐藏行表头

        self.timer_display = QTimer(self)   # 定时器，程序启动后延时显示数据
        self.timer_display.setSingleShot(True)  # 只启动一次
        self.timer_display.timeout.connect(self.display)  # 启动进程显示界面，避免程序启动时，数据检索导致堵塞
        self.timer_display.start(10)  # 程序启动10毫秒后执行

        self.display_thread = DisplayThread()
        self.display_thread.trigger.connect(self.display_post)

        self.timer_task = QTimer(self)  # 定时器，程序启动后延时显示数据
        self.timer_task.timeout.connect(self.task)  # 启动进程显示界面，避免程序启动时，数据检索导致堵塞
        self.timer_task.start(5*1000)  # 每隔1分启动一次
        self.timer_task.setSingleShot(True)  # 只启动一次
        self.task_thread = TaskThread(self.transinfo_list)
        self.task_thread.trigger.connect(self.task_post)

        # 初始化时间和查询范围
        self.set_time_and_range()

        # 日志数据
        self.model = QtGui.QStandardItemModel()
        # 设置数据模型
        self.tableView_log.setModel(self.model)

        # 树点击事件
        self.treeWidget_menu.clicked.connect(self.set_translog)
        # 过滤按钮点击事件
        self.pushButton_query.clicked.connect(self.set_translog)
        # 手动传输按钮点击时间
        self.pushButton_manual.clicked.connect(self.manual)
        # 设置按钮事件
        self.pushButton_setting.clicked.connect(self.setting)
        # 退出按钮
        self.pushButton_quit.clicked.connect(self.close)
        # 自适应列宽
        self.tableView_log.resizeColumnsToContents()

        # 设置传输菜单界面
        self.treeWidget_menu.setColumnCount(2)
        self.treeWidget_menu.setHeaderLabel('数据传输列表')
        # 隐藏接口类型列
        self.treeWidget_menu.header().setSectionHidden(1, True)
        self.treeWidget_menu.expandAll()

    def display(self):
        """启动程序若干毫秒后进行异步检索线程"""
        self.display_thread.start()

    def display_post(self, signal):
        if not signal:
            return
        try:
            translist = signal.get("translist", None)
            if translist:
                self.set_transinfo(translist)
                #
                self.set_translog()
        except Exception as e:
            showmsg(str(e))

    def task(self):
        self.task_thread.transtype_list = self.transinfo_list
        self.task_thread.start()

    def task_post(self, signal):
        if signal:
            self.set_translog()

    def set_time_and_range(self):

        # 日期选择空间
        self.dateTimeEdit_begin.setCalendarPopup(True)
        self.dateTimeEdit_end.setCalendarPopup(True)

        now = datetime.datetime.now()
        # 设置日期及日期格式
        self.dateTimeEdit_begin.setDate(now)
        self.dateTimeEdit_end.setDate(now)
        self.dateTimeEdit_begin.setDisplayFormat('yyyy-MM-dd')
        self.dateTimeEdit_end.setDisplayFormat('yyyy-MM-dd')
        # 设置时间及时间格式
        self.timeEdit_begin.setTime(datetime.time(0, 0, 0))
        self.timeEdit_end.setTime(datetime.time(23, 59, 59))
        self.timeEdit_begin.setDisplayFormat('hh:mm:ss')
        self.timeEdit_end.setDisplayFormat('hh:mm:ss')
        # 设置查询范围
        range_status = TransModelInit.trans_status_choice
        for num, status in enumerate(range_status.keys()):
            self.comboBox_ramge.addItem(status)
            self.comboBox_ramge.setItemData(num, range_status.get(status, ''))
        self.comboBox_ramge.setCurrentIndex(0)

    def set_transinfo(self, param):
        transinfo_list = param
        # 设置属性传输列表，避免定时器触发时检索
        self.transinfo_list = transinfo_list
        print(self.transinfo_list)

        level_list = sorted(set([x.lvl for x in transinfo_list]))
        for level in level_list:
            transinfo = [x for x in transinfo_list if x.lvl == level]
            transinfo = sorted(transinfo, key=lambda t: t.srlid)
            for trans in transinfo:
                if level == min(level_list) and trans.prtno == '*':
                    item = QTreeWidgetItem(self.treeWidget_menu)
                    item.setText(0, trans.text)
                    item.setText(1, trans.no)
                    self.treeWidget_menu.addTopLevelItem(item)
                    self.treeWidget_menu.setCurrentItem(item)
                else:
                    parent = trans.prtno
                    item = self.treeWidget_menu.findItems(parent, Qt.MatchRecursive, 1)
                    if item:
                        child = QTreeWidgetItem(item[0])
                        child.setText(0, trans.text)
                        child.setText(1, str(trans.no))

        self.treeWidget_menu.expandAll()
        return True, None

    def set_translog(self):
        """设置传输日志"""
        # 开始时间
        begin_time = "{} {}".format(self.dateTimeEdit_begin.text(), self.timeEdit_begin.text())
        # 结束时间
        end_time = "{} {}".format(self.dateTimeEdit_end.text(), self.timeEdit_end.text())
        # 状态
        status = self.comboBox_ramge.currentData()
        status = TransModelInit.trans_status_choice.get(status, '')
        # 类型
        no = self.treeWidget_menu.currentItem().text(1)
        self.model.clear()
        # 获取数据库数据
        result, translog_list = self._provider.get_trans_log(begin_time=begin_time, end_time=end_time, status=status, no=no)
        if not result:
            return result, translog_list


        headers = ("接口状态", "接口类型", "开始时间", "结束时间", "影响行数", "错误原因")
        self.model.setHorizontalHeaderLabels(headers)
        self.model.setRowCount(len(translog_list))
        self.model.setColumnCount(len(headers))
        choice = TransModelInit.trans_status_choice
        choice_reverse = {v: k for k, v in choice.items()}
        for row_num, translog in enumerate(translog_list):

            status = translog.status
            status = choice_reverse.get(status, '')
            text = translog.text
            begin_time = translog.begin_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            end_time = translog.end_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            trans_count = translog.trans_count or 0
            msg = translog.msg or ''

            cols = [status, text, begin_time, end_time, trans_count, msg]
            for col_num, col in enumerate(cols):
                col_value = str(col)
                item = QtGui.QStandardItem(col_value)
                if choice.get(status, '') == '0':
                    item.setForeground(Qt.red)
                self.model.setItem(row_num, col_num, item)
        # 排序
        self.model.sort(2, order=Qt.DescendingOrder)

        # 根据内容自适应列宽
        self.tableView_log.resizeColumnsToContents()
        header = self.tableView_log.horizontalHeader()
        # 避免过去拥挤，每列设置一些空隙
        for i in range(header.count()):
            self.tableView_log.setColumnWidth(i, self.tableView_log.columnWidth(i) + 40)
        # 最后一列补全剩下空隙
        header.setStretchLastSection(True)

    def create_trayicon(self):
        """创建托盘"""

        # 显示按钮
        restoreaction = QAction("&显示", self, triggered=self.showNormal)
        # 退出按钮
        quitaction = QAction("&退出", self, triggered=self.close)
        # 托盘菜单
        self.trayiconmenu.addAction(restoreaction)
        self.trayiconmenu.addAction(quitaction)
        self.trayicon.setContextMenu(self.trayiconmenu)
        # 设置帮助信息
        self.trayicon.setToolTip(self.windowTitle())

        # 设置图标
        self.trayicon.setIcon(self.icon)
        self.setWindowIcon(self.icon)
        self.trayicon.activated[QSystemTrayIcon.ActivationReason].connect(self.iconactivated)

    def iconactivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isHidden():
                self.showNormal()
            else:
                self.hide()

    def changeEvent(self, event):
        """最小化事件，改为隐藏到托盘"""
        if event.type() == QEvent.WindowStateChange and self.isMinimized():
            self.hide()
            self.trayicon.show()

    def closeEvent(self, event):
        """关闭事件，只有窗口隐藏状态下才能关闭串口"""
        if not self.isHidden():
            self.hide()
            self.trayicon.show()
            event.ignore()
        else:
            try:
                ret = showmsg("程序正在运行，是否关闭？", type=QMessageBox.Question)
                if ret != QMessageBox.Ok:
                    event.ignore()
                else:
                    event.accept()
            except Exception as e:
                showmsg(str(e), QMessageBox.Critical)

    def manual(self):
        """手动传输"""
        try:
            self._manual = TransManual(self.transinfo_list)
            self._manual.show()
        except Exception as e:
            showmsg(str(e), type=QMessageBox.Critical)

    def setting(self):
        """设置"""
        try:
            if not self._setting:
                self._setting = TransSetting(self.transinfo_list)
            self._setting.show()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))


class DisplayThread(QThread):
    """获取运行时参数，包括数据库和config文件"""
    # 定义一个信号
    trigger = pyqtSignal(dict)

    def run(self):
        """异步获取，获取运行时信息"""
        _provider = TransDataProvider()  # 数据库数据提供对象
        result, translist = _provider.get_trans_list()  # 获取传输列表
        if not result:
            showmsg(translist, type=QMessageBox.Critical)
        else:
            signal = dict(translist=translist)
            self.trigger.emit(signal)


class TaskThread(QThread):
    """自动运行任务"""
    # 定义一个信号，表示任务完成，需要刷新界面
    trigger = pyqtSignal(bool)

    def __init__(self, transtype_list):
        super(QThread, self).__init__()
        self.transtype_list = transtype_list

    def run(self):
        """异步获取，获取运行时信息"""
        try:
            auto_begin_task(self.transtype_list)
            signal = True
            self.trigger.emit(signal)
        except Exception as e:
            self.trigger.emit(False)



def f_main():
    """主程序，保证程序单实例运行"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    servername = "TransTools"

    socket = QLocalSocket()
    socket.connectToServer(servername)
    if socket.waitForConnected(500):
        # 程序只允许单例运行
        showmsg("程序已运行！")
        return(app.quit())

    # 没有实例运行，创建服务器
    localServer = QLocalServer()
    localServer.listen(servername)

    try:
        main = Main()
        main.show()

        sys.exit(app.exec_())
    except Exception as e:
        showmsg(str(e), type=QMessageBox.Critical)
    finally:
        localServer.close()


if __name__ == "__main__":
    f_main()



