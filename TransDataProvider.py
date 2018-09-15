from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from TransConfiger import Config
from TransModels import TransType, Base, TransLog, TransModelInit


class TransDataBase:
    """ 初始化传输数据 """

    def __init__(self):
        self._config = Config()
        self.init_db()
        self.init_table()

    def get_orm_engine(self, engine_name=None):
        """获取orm引擎"""
        engine = None
        if engine_name is None:
            engine_name = 'default'

        result, config = self._config.get_orm_engine(engine_name)
        if not result:
            return result, config
        if result:
            engine = create_engine(config["engine"])
        return True, engine

    def init_db(self):
        """创建传输工具所需要的基础表"""
        result, engine = self.get_orm_engine()
        if not result:
            return result, engine
        Base.metadata.create_all(engine)

    def init_table(self):
        """往传输工具表中写入基础数据"""
        result, engine = self.get_orm_engine()
        if not result:
            return result, engine
        session = sessionmaker(bind=engine)()
        #  写入基础数据
        if session.query(TransType).count() > 0:
            session.close()
            return
        else:
            session.bulk_save_objects(TransModelInit.get_init_translist())
            session.commit()
            session.close()


class TransDataProvider:
    """传输工具数据提供接口"""
    def __init__(self):
        self.config_path = 'TransTools.yaml'    # 配置文件名称
        self.databases = 'databases'             # 配置文件数据库节点名称
        self.default = 'default'                 # 配置文件默认节点名称
        self.proc = 'ts_pr_sys_trans'           # 数据库存储过程
        self.proc_log = 'ts_pr_sys_trans_log'  # 数据库日志处理存储过程
        self.table = "ts_t_sys_funclist"        # 数据库传输表
        self._config = Config()

    def get_orm_engine(self, engine_name=None):
        """获取orm引擎"""
        engine = None
        if engine_name is None:
            engine_name = 'default'

        result, config = self._config.get_orm_engine(engine_name)
        if not result:
            return result, config
        if result:
            if engine_name == 'oracle':
                engine = create_engine(config["engine"], encoding='gbk', use_ansi=False)
            else:
                engine = create_engine(config["engine"])
        return True, engine

    def get_orm_session(self,engine_name=None):
        result, engine = self.get_orm_engine(engine_name)
        if not result:
            return result, engine
        session = sessionmaker(bind=engine)()
        return True, session

    def get_trans_list(self):
        """获取传输接口"""
        try:
            result, session = self.get_orm_session()
            if not result:
                return result, session
            return True, session.query(TransType).all()
        except Exception as e:
            return False, repr(e)

    def set_trans_list(self, transtype_list):
        """更新传输接口"""
        try:
            result, session = self.get_orm_session()
            if not result:
                return result, session
            for transtype in transtype_list:
                session.query(TransType).filter(TransType.no==transtype.no).update({
                    TransType.space_type: transtype.space_type,
                    TransType.space_time: transtype.space_time,
                    TransType.start_hour: transtype.start_hour,
                    TransType.end_hour: transtype.end_hour,
                    TransType.trans_type: transtype.trans_type
                })
                session.commit()
            session.close()
            return True, None
        except Exception as e:
            return False, repr(e)

    def get_trans_log(self, *args, **kwargs):
        """获取传输日志列表"""
        result, session = self.get_orm_session()
        if not result:
            return result, sessions
        result = session.query(TransLog)
        if kwargs.get("no", None):
            result = result.filter(TransLog.no.like('{}%'.format(kwargs["no"])))
        if kwargs.get("begin_time",None):
            result = result.filter(TransLog.begin_time >= kwargs["begin_time"])
        if kwargs.get("end_time", None):
            result = result.filter(TransLog.end_time <= kwargs["end_time"])
        if kwargs.get("status", ''):
            result = result.filter(TransLog.status == kwargs["status"])

        return True, result.all()


if __name__ == "__main__":
    # provider = TransDataProvider()
    # print(provider.get_trans_log(status="1", begin_time="2018-09-12"))
    pass


