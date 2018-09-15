import datetime
from multiprocessing.pool import ThreadPool
from PyQt5.QtWidgets import QMessageBox, QGridLayout
from TransModels import TransLog, TransType
from TransTask import TransTask
from TransDataProvider import TransDataProvider

threadpool = ThreadPool()

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
        result, data = func(*args, **kwargs)
        print(result, data)
        end_time = datetime.datetime.now()
        trans_count = 0
        trans_msg = ""
        task_name = args[0]  # 传输名称
        if result:
            trans_count = data
            trans_status = "1"
        else:
            trans_msg = data
            trans_status = "0"

        result_s, session = TransDataProvider().get_orm_session()
        text, no = session.query(TransType.text, TransType.no).filter(TransType.sheetid==task_name).first()
        translog = TransLog(status=trans_status, begin_time=begin_time,end_time=end_time,
                            trans_count=trans_count, sheetid=task_name, msg=trans_msg, text=text, no=no)

        if result_s:
            session.add(translog)
            session.commit()

        return result, data
    return _log


@tasklog
def begin_task(task_name):
    task_class_list = TransTask.__subclasses__()
    task_class = [tsk for tsk in task_class_list if tsk.__name__ == task_name]
    if not task_class:
        return False, "不支持的传输任务类型{}，请先进行类型定义".format(task_name)
    task = task_class[0]()
    return task.run()


def auto_begin_task(transtype_list):
    """自动传输"""
    if not transtype_list:
        return True, None

    transtype_list_shouldrun = [transtype for transtype in transtype_list if transtype.is_should_run()]
    for transtype in transtype_list_shouldrun:
        sheetid = transtype.sheetid
        threadpool.map(begin_task, (sheetid,))







