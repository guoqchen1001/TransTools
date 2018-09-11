import threading


class TransTask(threading.Thread):
    """传输任务线程"""
    def __init__(self, transname):
        super(TransTask, self).__init__()
        self.name = transname

    def run(self):
        pass

    def execute(self):
        pass







