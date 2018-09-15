import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListWidgetItem
from manual import Ui_Dialog
from TransDataProvider import TransDataProvider
from TransBaseFunc import showmsg, begin_task


class TransManual(QtWidgets.QDialog, Ui_Dialog):
    """手动传输界面"""
    def __init__(self, translist=None):
        super(TransManual, self).__init__()
        self.setupUi(self)
        # 数据提供实例
        self._provider = TransDataProvider()
        # 传输列表
        if not translist:
            result, translist = self._provider.get_trans_list()
            if not result:
                return
        self._translist = translist
        # 显示列表
        self.listviews = []
        # 确定事件
        self.accepted.connect(self.trans)
        # 每页显示条数
        self.pagenum = 20
        self.display()

    def display(self):
        """设置界面接口信息"""
        # 接口数
        sheetlist = [x for x in self._translist if x.sheetid]
        length = len(sheetlist)
        # 每页的接口数量
        pagenum = self.pagenum
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
        if not self.listviews:
            return True, ''
        for listview in self.listviews:
            for i in range(listview.count()):
                item = listview.item(i)
                if not item.checkState():
                    continue
                sheetid = item.data(1)
                try:
                    begin_task(sheetid)
                except Exception as e:
                    print(str(e))

        showmsg("传输完成")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    manul = TransManual()
    manul.show()
    sys.exit(app.exec_())

