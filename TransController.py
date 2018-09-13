import datetime
import threading
from TransDataProvider import TransDataProvider
import os
import ftplib
from PyQt5.QtWidgets import QMessageBox,QGridLayout


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


class TransLogging:
    """日志记录"""
    def __init__(self):
        pass

    def __call__(self, func):
        def _call(*args, **kwargs):
            _provider = TransDataProvider()
            begin_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 记录最后一次运行时间
            _provider.set_trans_opertime(*args, **kwargs)
            ret = func(*args, **kwargs)
            # 记录运行结果
            end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # 执行结果
            kwargs['rtncode'] = ret[0]
            # 执行信息
            kwargs['rtnmsg'] = ret[1]
            # 开始时间
            kwargs['begin_time'] = begin_time
            # 结束时间
            kwargs['end_time'] = end_time
            _provider.set_trans_operinfo(*args, **kwargs)
            return ret
        return _call


class TransController:

    def __init__(self):
        self._provider = TransDataProvider()
        self.file_dir = 'file'


    @staticmethod
    def get_ftp_filename(filetype, company, brhno=None):
        """ 获取FTP文件名 """
        filetype = filetype.upper()
        if brhno is None:
            brhno = ""
        now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        return '{}-{}{}-{}.TXT'.format(filetype, company, brhno, now)

    @staticmethod
    def get_ftp_format_data(data):
        """格式化ftp传输数据"""
        # 字段之间tab分割
        char_split_str = '\t'
        # 行之间 回车换行分割
        line_split_str = '\r\n'
        result = [char_split_str.join(map(str, row)) for row in data]
        return line_split_str.join(map(str, result))

    def send_ftp_file(self, f, file_name, file_dir=None):
        """发送文件到ftp服务器"""
        if file_dir is None:
            file_dir = self.file_dir
        # 检测ftp路径是否存在，不存在则创建
        file_full_dir = os.path.join(os.getcwd(), file_dir)
        if not os.path.exists(file_full_dir):
            os.mkdir(file_full_dir)
        full_file_name = os.path.join(file_full_dir, file_name)

        # 获取配置文件中ftp信息
        result, ftp_info = self._provider.get_ftp_connect()
        if not result:
            return result, ftp_info

        # 发送文件至ftp服务器
        try:
            buffersize = 1024
            with ftplib.FTP(ftp_info['url']) as ftp:
                ftp.login(ftp_info['user'], ftp_info['pwd'])
                with open(full_file_name, 'rb') as f:
                    ftp.storbinary("STOR " + file_name, f, buffersize)
                    return True, ''
        except Exception as e:
            err_msg = "文件{}FTP传输失败：{}".format(file_name, str(e))
            return False, err_msg

    def save_ftp_file(self, data, filename, file_dir=None):
        """生成ftp传输文件, 此文件在本地留存一份，以便比对"""
        if file_dir is None:
            file_dir = self.file_dir
        try:
            # 保存本地文件
            file_full_dir = os.path.join(os.getcwd(), file_dir)
            if not os.path.exists(file_full_dir):
                os.mkdir(file_full_dir)
            full_file_name = os.path.join(file_full_dir, filename)
            with open(full_file_name, 'w', encoding='utf-8') as f:
                f.write(data)
                return True, ''
        except Exception as e:
            return False, str(e)

    @TransLogging()
    def trans(self, *args, **kwargs):
        # 获取传输数据
        filetype = kwargs['transtype']
        result, data = self._provider.get_tran_data(filetype)
        # 结果条数
        if not result:
            return result, data
        result_count = len(data)
        if not data:
            return result, len(data)
        # 获取公司信息
        result, company = self._provider.get_company()
        if not result:
            return result, company
        # 获取文件名称
        filename = self.get_ftp_filename(filetype, company)
        # 格式化传输数据
        data = self.get_ftp_format_data(data)
        # 保存本地文件
        result, msg = self.save_ftp_file(data, filename)
        if not result:
            return result, msg

        # 传输ftp文件
        result, msg = self.send_ftp_file(data, filename)
        if not result:
            return result, msg
        return True, result_count

    def task(self):
        """自动传输任务"""
        result, task_list = self._provider.get_trans_list()
        if not result:
            return result, task_list
        for task in task_list:
            start_hour = task["fstart_hour"]  # 开始时间  hour：00：00
            end_hour = task["fend_hour"]  # 结束时间 hour:59:59
            trans_model = task['ftrans_type']  # 传输类型 1/自动 0/手动
            max_date = task['flast_datetime']  # 最后一次传输时间
            space_type = task['fspace_type']  # 间隔类型 间隔类型 0/小时 1/分钟
            space_time = task['fspace_time']  # 传输间隔
            fun_name = task['fsheetid']  # 传输接口名称
            # 接口不存在，则退出
            if not fun_name:
                continue
            # 计算间隔秒钟
            if space_type == '0':
                space_seconds = space_time*60*60
            else:
                space_seconds = space_time*60
            now = datetime.datetime.now()
            now_hour = now.hour
            # 非自动传输则退出
            if trans_model != '0':
                continue
            # 没到传输时间则退出
            if now_hour > end_hour or now_hour < start_hour:
                continue
            # 如果时间间隔未达到设置间隔则退出
            if max_date:
                if (now - max_date).seconds < space_seconds:
                    continue
            # 启动线程
            t = threading.Thread(target=self.trans, args=(fun_name,), kwargs={'transtype': fun_name})
            t.start()

    def task_manual(self, translist):
        """手动传输"""

        # 启动线程
        for trans in translist:
            t = threading.Thread(target=self.trans, args=(trans,), kwargs={'transtype': trans })
            t.start()

