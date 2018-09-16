import datetime
from multiprocessing.pool import ThreadPool
from PyQt5.QtWidgets import QMessageBox, QGridLayout
from TransModels import TransLog, TransType
from TransTask import TransTask
from TransDataProvider import TransDataProvider

threadpool = ThreadPool()


class NotSupporTransType(Exception):

    def __init__(self,task_name):
        self.task_name = task_name

    def __str__(self):
        return "不支持的传输类型[{}]".format(self.task_name)


def showmsg(showmsg, detailmsg=None, type=None, default=None):
    msgbox = QMessageBox()
    # 标题
    title = "数据传输中心"
    # 消息类型
    if type is None:
        type = QMessageBox.Information
    msgbox.setWindowTitle(title)
    # 显示信息
    msgbox.setText(showmsg)
    # 详细信息
    if detailmsg is not None:
        msgbox.setDetailedText(detailmsg)
    msgbox.setIcon(type)
    # 选择样式
    if type == QMessageBox.Question:
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    # 默认按钮
    if default is None:
        default = QMessageBox.Ok
    msgbox.setDefaultButton(default)

    gridlayout = msgbox.findChild(QGridLayout)
    # 设置最小宽度
    gridlayout.setColumnMinimumWidth(2, 400)
    # 返回值
    ret = msgbox.exec_()
    return ret


def tasklog(func):
    def _log(*args, **kwargs):
        begin_time = datetime.datetime.now()
        try:
            result = func(*args, **kwargs)
            print(result)
            trans_msg = ""
            trans_status = '1'
            trans_count = int(result)

        except Exception as e:
            result = False
            trans_count = 0
            trans_msg = str(e)
            trans_status = '0'
        end_time = datetime.datetime.now()
        task_name = args[0]  # 传输名称

        session = TransDataProvider().get_orm_session()
        text, no = session.query(TransType.text, TransType.no).filter(TransType.sheetid == task_name).first()
        translog = TransLog(status=trans_status, begin_time=begin_time,end_time=end_time,
                            trans_count=trans_count, sheetid=task_name, msg=trans_msg, text=text, no=no)

        session.add(translog)
        session.commit()
        return result
    return _log


@tasklog
def begin_task(task_name):
    task_class_list = TransTask.__subclasses__()
    task_class = [tsk for tsk in task_class_list if tsk.__name__ == task_name]
    if not task_class:
        raise NotSupporTransType(task_name)
    task = task_class[0]()
    return task.run()


def auto_begin_task(transtype_list):
    """自动传输"""
    if not transtype_list:
        return None

    transtype_list_shouldrun = [transtype for transtype in transtype_list if transtype.is_should_run()]
    for transtype in transtype_list_shouldrun:
        sheetid = transtype.sheetid
        threadpool.map(begin_task, (sheetid,))



