import datetime
import sys
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QEvent, QThread, pyqtSignal
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtGui import QIntValidator, QIcon
from mainwindow import Ui_MainWindow
from manual import Ui_Dialog as Ui_Dialog_manual
from setting import Ui_Form as Ui_Form_setting
from TransController import TransController, showmsg
from TransDataProvider import TransDataProvider


class Main(QtWidgets.QMainWindow, Ui_MainWindow):
    """主窗口"""
    def __init__(self):

        super(Main, self).__init__()  # 初始化
        self.setupUi(self)

        self._provider = TransDataProvider()  # 数据提供对象
        self._controller = TransController()  # 业务控制对象

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

        # 初始化时间和查询范围
        self.set_time_and_range()

        # 日志数据
        self.model = QtGui.QStandardItemModel()
        # 设置数据模型
        self.tableView_log.setModel(self.model)

        # 树点击事件
        self.treeWidget_menu.clicked.connect(self.set_trans_log)
        # 过滤按钮点击事件
        self.pushButton_query.clicked.connect(self.set_trans_log)
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
        """启动程序启动后数据检索线程"""
        self.display_thread.start()

    def display_post(self, signal):
        if not signal:
            return
        translist = signal.get("translist", None)
        if translist:
            result, data = translist
            if not result:
                showmsg(data, type=QMessageBox.Critical)
                return result
            self.set_transinfo(data)

    def set_transinfo(self, data):
        transinfo_list = trans_info
        # 设置属性传输列表，避免定时器触发时检索
        self.transinfo_list = transinfo_list
        level_list = sorted(set([x['flvl'] for x in transinfo_list]))
        for level in level_list:
            transinfo = [x for x in transinfo_list if x['flvl'] == level]
            transinfo = sorted(transinfo, key=lambda t: t['fsrlid'])
            for trans in transinfo:
                if level == min(level_list) and trans['fprtno'] == '*':
                    item = QTreeWidgetItem(self.treeWidget_menu)
                    item.setText(0, trans['ftext'])
                    item.setText(1, trans['fno'])
                    self.treeWidget_menu.addTopLevelItem(item)
                    self.treeWidget_menu.setCurrentItem(item)
                else:
                    parent = trans['fprtno']
                    item = self.treeWidget_menu.findItems(parent, Qt.MatchRecursive, 1)
                    if item:
                        child = QTreeWidgetItem(item[0])
                        child.setText(0, trans['ftext'])
                        child.setText(1, str(trans['fno']))
        return True, None

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

    def set_time_and_range(self):
        now = datetime.datetime.now()
        # 设置日期及日期格式
        self.dateEdit_begin.setDate(now)
        self.dateEdit_end.setDate(now)
        self.dateEdit_begin.setDisplayFormat('yyyy-MM-dd')
        self.dateEdit_end.setDisplayFormat('yyyy-MM-dd')
        # 设置时间及时间格式
        self.timeEdit_begin.setTime(datetime.time(0, 0, 0))
        self.timeEdit_end.setTime(datetime.time(23, 59, 59))
        self.timeEdit_begin.setDisplayFormat('hh:mm:ss')
        self.timeEdit_end.setDisplayFormat('hh:mm:ss')
        # 设置查询范围
        range_list = ['失败','成功', '全部']
        for num, status in enumerate(range_list):
            self.comboBox_ramge.addItem(status)
            data = num
            if num + 1 == len(range_list):
                data = - 1
            self.comboBox_ramge.setItemData(num, data)
        self.comboBox_ramge.setCurrentIndex(len(range_list) - 1)

    def set_trans_log(self):
        """设置传输日志"""
        # 开始时间
        begin_date = self.dateEdit_begin.text()
        # 结束时间
        end_date = self.dateEdit_end.text()
        # 状态
        status = self.comboBox_ramge.currentData()
        # 类型
        sheetno = self.treeWidget_menu.currentItem().text(1)

        # 获取数据库数据
        result, data = self._provider.get_trans_log(begin_date=begin_date, end_date=end_date,sheetno=sheetno, status=status)
        if not result:
            return result, data
        # 总行数
        length = len(data)
        if length == 0:
            self.model.clear()
        headers = ("接口状态", "接口类型", "开始时间", "结束时间", "影响行数", "错误原因")
        cols = ("fstatus", "ftext", "fbegin_date","fend_date","ftrans_cnt","fmsg")
        self.model.setHorizontalHeaderLabels(headers)
        self.model.setRowCount(length)
        self.model.setColumnCount(len(headers))
        for number, row in enumerate(data):
            status = data[number][cols[0]]
            for i in range(len(cols)):
                value = str(data[number][cols[i]])
                item = QtGui.QStandardItem(value)
                if status == '失败':
                    item.setForeground(Qt.red)
                self.model.setItem(number, i, item)
        # 排序
        self.model.sort(2, order=Qt.DescendingOrder)
        # 自适应列宽
        self.tableView_log.resizeColumnsToContents()

    def manual(self):
        """手动传输"""
        try:
            self._manual = Manual(self.transinfo_list)
            self._manual.show()
        except Exception as e:
            showmsg(str(e),type=QMessageBox.Critical)

    def setting(self):
        """设置"""
        try:
            if not self._setting:
                self._setting = Setting(self.transinfo_list)
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
        result = _provider.get_trans_list()  # 获取传输列表
        signal = dict(translist=result)
        self.trigger.emit(signal)



class Manual(QtWidgets.QDialog, Ui_Dialog_manual):
    """手动传输界面"""
    def __init__(self, translist=None):
        super(Manual, self).__init__()
        self.setupUi(self)
        self._translist = translist
        self._controller = TransController()
        self.listviews = []
        self.accepted.connect(self.trans)
        self.set_translist()

    def set_translist(self):
        """设置界面接口信息"""
        # 接口数
        sheetlist = [x for x in self._translist if x['fsheetid']]
        length = len(sheetlist)
        # 每页的接口数量
        pagenum = 20
        page = length//pagenum
        if page == 0:
            page = 1
        for i in range(page):
            listview = QtWidgets.QListWidget()
            self.listviews.append(listview)
            self.hLayout.addWidget(listview)
            for j in range(i*pagenum, (i + 1)*pagenum):
                if j > length - 1:
                    continue
                sheetid = sheetlist[j]['fsheetid']
                funname = sheetlist[j]["ftext"]
                item = QListWidgetItem()
                item.setText(funname)
                item.setData(1, sheetid)
                item.setCheckState(False)
                listview.addItem(item)

    def trans(self):
        """手动传输"""
        translit = []
        _main = Main()
        if not self.listviews:
            return True, ''
        for listview in self.listviews:
            for i in range(listview.count()):
                item = listview.item(i)
                if not item.checkState():
                    continue
                sheetid = item.data(1)
                translit.append(sheetid)
        self._controller.task_manual(translit)
        _main.set_trans_log()
        showmsg("传输完成")


class Setting(QtWidgets.QWidget, Ui_Form_setting):
    """ 设置界面 """
    def __init__(self, translist=None):
        super(Setting, self).__init__()
        self.setupUi(self)
        self._translist = translist
        self._provider = TransDataProvider()
        self.pushButton_cancel.clicked.connect(self.hide)
        self.pushButton.clicked.connect(self.save)
        self.isinit = False  # 是否初始化完成
        self._translist_data = []  # 修改数据存放列表
        self.set_translist()
        self.set_trans_dsplay()
        self.set_trans_data()

    def set_translist(self):
        """获取设置参数"""
        if not self._translist:
            result, data = self._provider.get_trans_list()
            if not result:
                return result, data
            if not data:
                return True, data
            self._translist = data

    def set_trans_dsplay(self):
        """ 初始化界面控件 """
        tablist = [x for x in self._translist if x['fprtno'] == '*' ]
        for tab in tablist:
            tabname = tab["ftext"]
            tabno = tab["fno"]
            widget = QWidget()
            tranlist = [x for x in self._translist if x["fprtno"] == tabno]
            gridlayout = QGridLayout()
            gridlayout.setSpacing(12)
            for num, tran in enumerate(tranlist):
                # 传输id
                transid = tran["fsheetid"]
                # 水平位置
                row = num//3
                # 垂直位置
                col = num%3
                # 组合框
                groupbox = QGroupBox(tran["ftext"])
                # 组合框布局
                gridlayout_group = QGridLayout()
                # 开始时间
                lable_begin = QLabel()
                timeedit_begin = QTimeEdit()
                timeedit_begin.setDisplayFormat("hh:mm:00")
                timeedit_begin.setObjectName("{}_timedit_begin".format(transid))
                timeedit_begin.timeChanged.connect(self.change)
                lable_begin.setText("开始时间")
                gridlayout_group.addWidget(lable_begin,0,1)
                gridlayout_group.addWidget(timeedit_begin,0,2,1,2)
                # 结束时间
                lable_end = QLabel()
                timeedit_end = QTimeEdit()
                timeedit_end.setDisplayFormat("hh:mm:59")
                timeedit_end.setObjectName("{}_timedit_end".format(transid))
                timeedit_end.timeChanged.connect(self.change)
                lable_end.setText("结束时间")
                gridlayout_group.addWidget(lable_end, 1, 1)
                gridlayout_group.addWidget(timeedit_end, 1, 2, 1,2)
                # 手动/自动传输
                radiobutton_manual = QRadioButton()
                radiobutton_manual.setText("手动传输")
                radiobutton_manual.setObjectName("{}_radiobutton_manual".format(transid))
                radiobutton_manual.clicked.connect(self.change)
                radiobutton_auto = QRadioButton()
                radiobutton_auto.setText("自动动传输")
                radiobutton_auto.setObjectName("{}_radiobutton_auto".format(transid))
                radiobutton_auto.clicked.connect(self.change)
                gridlayout_group.addWidget(radiobutton_manual, 2, 1)
                gridlayout_group.addWidget(radiobutton_auto, 2, 2)
                # 传输间隔类型
                label_space = QLabel()
                label_space.setText("传输间隔")
                lineedit_space = QLineEdit()
                lineedit_space.setObjectName("{}_lineedit_space".format(transid))
                # 设置只允许输入数字
                objvalidator = QIntValidator(1, 14400)
                lineedit_space.setValidator(objvalidator)
                lineedit_space.textChanged.connect(self.change)
                combobox_space = QComboBox()
                combobox_space.setObjectName("{}_combobox_space".format(transid))
                combobox_space.addItem("小时")
                combobox_space.setItemData(0, 0)
                combobox_space.addItem("分钟")
                combobox_space.setItemData(1, 1)
                combobox_space.setCurrentIndex(1)
                combobox_space.currentIndexChanged.connect(self.change)
                gridlayout_group.addWidget(label_space, 3, 1)
                gridlayout_group.addWidget(lineedit_space, 3, 2)
                gridlayout_group.addWidget(combobox_space, 3, 3)

                # 设置间距
                gridlayout_group.setHorizontalSpacing(10)
                gridlayout_group.setVerticalSpacing(10)
                gridlayout_group.setContentsMargins(10, 10, 10, 10)
                # 添加到组合框
                groupbox.setLayout(gridlayout_group)
                gridlayout.addWidget(groupbox, row, col)

            widget.setLayout(gridlayout)
            self.tabWidget.addTab(widget, tabname)

    def set_trans_data(self):
        """ 设置界面数据 """
        translist = [x for x in self._translist if x["fsheetid"]]
        for trans in translist:
            begin_hour = trans["fstart_hour"]
            end_hour = trans["fend_hour"]
            transtype = trans["ftrans_type"]
            transid = trans["fsheetid"]
            space_type = trans['fspace_type']
            space_time = trans['fspace_time']
            timeedit_begin = self.findChild((QTimeEdit,), "{}_timedit_begin".format(transid) )
            timeedit_begin.setTime(datetime.time(begin_hour, 0, 0))
            timeedit_end = self.findChild((QTimeEdit,), "{}_timedit_end".format(transid))
            timeedit_end.setTime(datetime.time(end_hour, 59, 59))
            radiobutton_auto = self.findChild((QRadioButton,), "{}_radiobutton_auto".format(transid))
            radiobutton_manual = self.findChild((QRadioButton,), "{}_radiobutton_manual".format(transid))
            combobox_space = self.findChild((QComboBox,),'{}_combobox_space'.format(transid))
            lineedit_space = self.findChild((QLineEdit,), '{}_lineedit_space'.format(transid))
            lineedit_space.setText(str(space_time))
            if transtype == "1":
                radiobutton_auto.setChecked(False)
                radiobutton_manual.setChecked(True)
            else:
                radiobutton_auto.setChecked(True)
                radiobutton_manual.setChecked(False)

            if space_type == '1':
                combobox_space.setCurrentIndex(1)
            else:
                combobox_space.setCurrentIndex(0)
        self.isinit = True  # 初始化完成

    def change(self):
        """ 界面改动出发事件"""
        # 界面未初始化赋值时不需要出发此事件
        if not self.isinit:
            return

        data = {}
        try:
            # 触发该事件的对象
            sender = self.sender()
            # 对象名称
            name = sender.objectName()
            # 传输
            sheetid = name.split("_")[0]
            data["fsheetid"] = sheetid
            # time控件
            if isinstance(sender, QTimeEdit):
                hour = sender.text().split(":")[0]
                if name.split("_")[2] == "begin":
                    data["fstart_hour"] = int(hour)
                if name.split("_")[2] == "end":
                    data["fend_hour"] = int(hour)
            # radio控件
            if isinstance(sender, QRadioButton):
                if name.split("_")[2] == "manual":
                    data["ftrans_type"] = "1"
                if name.split("_")[2] == "auto":
                    data["ftrans_type"] = "0"
            # lineeidt
            if isinstance(sender,QLineEdit):
                space_time = sender.text()
                if not space_time:
                    return
                if not space_time.isdigit():
                    return
                if name.split('_')[2] == 'space':
                    data["fspace_time"] = int(space_time)

            if isinstance(sender, QComboBox):
                space_type = sender.currentData()
                if name.split('_')[2] == 'space':
                    data["fspace_type"] = str(space_type)

            # 如果已经存在，则改变状态
            data_exists = [x for x in self._translist_data if x["fsheetid"] == sheetid]
            if data_exists:
                index = self._translist_data.index(data_exists[0])
                self._translist_data[index].update(data)
            else:
                self._translist_data.append(data)
        except Exception as e:
            showmsg(str(e), type=QMessageBox.Critical)

    def save(self):
        """保存设置"""
        result, msg = self._provider.update_setting(self._translist_data)
        if result:
            self._translist_data = []
            showmsg("保存成功！")
        else:
            showmsg(str(e), type=QMessageBox.Critical)


def main():
    """主程序，保证程序单实例运行"""
    app = QtWidgets.QApplication(sys.argv)
    servername = "ftp_crm_trans"

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
    main()



