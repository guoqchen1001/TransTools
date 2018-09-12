import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator
from setting import Ui_Form
from TransDataProvider import TransDataProvider


class TransSetting(QtWidgets.QWidget, Ui_Form):
    """ 设置界面 """
    def __init__(self, translist=None):
        super(TransSetting, self).__init__()
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
            result = self._provider.get_trans_list()
            if result:
                self._translist = result

    def set_trans_dsplay(self):
        """ 初始化界面控件 """
        if not self._translist:
            return
        lvl_list = sorted(set([x.lvl for x in self._translist]))
        tablist = [x for x in self._translist if x.lvl == lvl_list[-2] ]
        for tab in tablist:
            tabname = tab.text
            tabno = tab.no
            widget = QWidget()
            tranlist = [x for x in self._translist if x.prtno == tabno]
            gridlayout = QGridLayout()
            gridlayout.setSpacing(12)
            for num, tran in enumerate(tranlist):
                # 传输id
                transid = tran.sheetid
                # 水平位置
                row = num // 3
                # 垂直位置
                col = num % 3
                # 组合框
                groupbox = QGroupBox(tran.text)
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
        translist = [x for x in self._translist if x.sheetid]
        for trans in translist:
            begin_hour = trans.start_hour or 0
            end_hour = trans.end_hour or 0
            transtype = trans.trans_type
            transid = trans.sheetid
            space_type = trans.space_type
            space_time = trans.space_time or 0
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
            data.sheetid = sheetid
            # time控件
            if isinstance(sender, QTimeEdit):
                hour = sender.text().split(":")[0]
                if name.split("_")[2] == "begin":
                    data.start_hour = int(hour)
                if name.split("_")[2] == "end":
                    data.end_hour = int(hour)
            # radio控件
            if isinstance(sender, QRadioButton):
                if name.split("_")[2] == "manual":
                    data.trans_type = "1"
                if name.split("_")[2] == "auto":
                    data.trans_type = "0"
            # lineeidt
            if isinstance(sender, QLineEdit):
                space_time = sender.text()
                if not space_time:
                    return
                if not space_time.isdigit():
                    return
                if name.split('_')[2] == 'space':
                    data.space_time = int(space_time)

            if isinstance(sender, QComboBox):
                space_type = sender.currentData()
                if name.split('_')[2] == 'space':
                    data.space_type = str(space_type)

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
