from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListWidgetItem
from manual import Ui_Dialog
from TransController import TransController


class TransManual(QtWidgets.QDialog, Ui_Dialog):
    """手动传输界面"""
    def __init__(self, translist=None):
        super(TransManual, self).__init__()
        self.setupUi(self)
        self._translist = translist
        self._controller = TransController()
        self.listviews = []
        self.accepted.connect(self.trans)
        self.set_translist()

    def set_translist(self):
        """设置界面接口信息"""
        # 接口数
        sheetlist = [x for x in self._translist if x.sheetid]
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
                sheetid = sheetlist[j].sheetid
                funname = sheetlist[j].text
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


