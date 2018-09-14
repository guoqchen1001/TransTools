import datetime
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator
from setting import Ui_Form
from TransDataProvider import TransDataProvider
from TransModels import TransType
from TransController import showmsg

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
        self.pertab_num = 9  # 一个tab页显示9行数据
        self.transgroupbox_list = []
        self.dusplay()


    def dusplay(self):
        """获取设置参数"""
        if not self._translist:
            result, translist = self._provider.get_trans_list()
            if result:
                self._translist = translist
            else:
                return result, translist

        self.set_trans_dsplay()

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
            if len(tranlist) < self.pertab_num:
                tranlist.extend(TransType() for i in range(self.pertab_num - len(tranlist)))
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
                transgroupbox = TransGroupBox(tran)
                gridlayout.addWidget(transgroupbox.groupbox, row, col)
                self.transgroupbox_list.append(transgroupbox)

            widget.setLayout(gridlayout)
            self.tabWidget.addTab(widget, tabname)

    def save(self):
        """保存设置"""
        try:
            transtype_list = []
            for transgroupbox in self.transgroupbox_list:
                transgroupbox.save()
                transtype_list.append(transgroupbox.transtype)
            result, data = self._provider.set_trans_list(transtype_list)
            if result:
                showmsg("保存成功")
            else:
                showmsg(data)
        except Exception as e:
            showmsg(repr(e))


class TransGroupBox(QWidget):
    """通过传输模型获取组合框，用于显示和设置传输"""
    def __init__(self, transtype):
        super(TransGroupBox, self).__init__()
        self.transtype = transtype
        self.initUI()

    def initUI(self):
        self.groupbox = QGroupBox()
        self.gridlayout = QGridLayout()

        # 开始时间
        self.timeedit_begin = QTimeEdit()
        self.lable_begin = QLabel()
        self.timeedit_begin.setDisplayFormat("hh:mm:00")
        self.lable_begin.setText("开始时间")

        # 结束时间
        self.lable_end = QLabel()
        self.timeedit_end = QTimeEdit()
        self.timeedit_end.setDisplayFormat("hh:mm:59")
        self.lable_end.setText("结束时间")

        # 手动/自动传输
        self.radiobutton_manual = QRadioButton()
        self.radiobutton_manual.setText("手动传输")
        self.radiobutton_auto = QRadioButton()
        self.radiobutton_auto.setText("自动传输")

        # 传输间隔类型
        self.label_space = QLabel()
        self.label_space.setText("传输间隔")
        self.lineedit_space = QLineEdit()

        # 设置只允许输入数字
        objvalidator = QIntValidator(1, 14400)
        self.lineedit_space.setValidator(objvalidator)

        # 间隔类型
        self.combobox_space = QComboBox()
        self.combobox_space.addItem("小时")
        self.combobox_space.setItemData(0, 0)
        self.combobox_space.addItem("分钟")
        self.combobox_space.setItemData(1, 1)
        self.combobox_space.setCurrentIndex(1)

        # 设置布局间距
        self.gridlayout.setHorizontalSpacing(10)
        self.gridlayout.setVerticalSpacing(10)
        self.gridlayout.setContentsMargins(10, 10, 10, 10)

        if self.transtype.sheetid:
            self.gridlayout.addWidget(self.lable_begin, 0, 1)
            self.gridlayout.addWidget(self.timeedit_begin, 0, 2, 1, 2)
            self.gridlayout.addWidget(self.lable_end, 1, 1)
            self.gridlayout.addWidget(self.timeedit_end, 1, 2, 1, 2)
            self.gridlayout.addWidget(self.radiobutton_manual, 2, 1)
            self.gridlayout.addWidget(self.radiobutton_auto, 2, 2)
            self.gridlayout.addWidget(self.label_space, 3, 1)
            self.gridlayout.addWidget(self.lineedit_space, 3, 2)
            self.gridlayout.addWidget(self.combobox_space, 3, 3)

        # 添加到组合框
        self.groupbox.setLayout(self.gridlayout)
        self.groupbox.setTitle(self.transtype.text)

        # 组合框布局
        transid = self.transtype.sheetid
        if transid:
            # 开始时间
            self.timeedit_begin.setObjectName("{}_timedit_begin".format(transid))
            start_hour = self.transtype.start_hour or 0
            self.timeedit_begin.setTime(datetime.time(start_hour, 0, 0))

            self.timeedit_end.setObjectName("{}_timedit_end".format(transid))
            end_hour = self.transtype.end_hour or 0
            self.timeedit_end.setTime(datetime.time(end_hour, 0, 0))

            self.radiobutton_manual.setObjectName("{}_radiobutton_manual".format(transid))
            self.radiobutton_auto.setObjectName("{}_radiobutton_auto".format(transid))
            if self.transtype.trans_type:
                self.radiobutton_auto.setChecked(True)
                self.radiobutton_manual.setChecked(False)
            else:
                self.radiobutton_auto.setChecked(False)
                self.radiobutton_manual.setChecked(True)

            space_time = self.transtype.space_time
            self.lineedit_space.setObjectName("{}_lineedit_space".format(transid))
            if space_time:
                self.lineedit_space.setText(str(space_time))

            space_type = self.transtype.space_type or '0'
            self.combobox_space.setObjectName("{}_combobox_space".format(transid))
            self.combobox_space.setCurrentIndex(int(space_type))

    def save(self):
        self.transtype.start_hour = self.timeedit_begin.time().hour()
        self.transtype.end_hour = self.timeedit_end.time().hour()
        self.transtype.space_type = self.combobox_space.currentData()
        self.transtype.space_time = self.lineedit_space.text()
        self.transtype.trans_type = self.radiobutton_manual.isCheckable()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    setting = TransSetting()
    setting.show()
    sys.exit(app.exec_())
