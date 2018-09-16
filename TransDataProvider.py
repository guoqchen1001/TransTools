from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from TransConfiger import Config
from TransModels import TransType, Base, TransLog, TransModelInit


class InitDBTableError(Exception):
    pass



class TransDataBase:
    """ 初始化传输数据 """

    def __init__(self):
        self._config = Config()

        self.init_db()
        self.init_table()

    def get_orm_engine(self, engine_name=None):
        """获取orm引擎"""
        config = self._config.get_orm_engine(engine_name)
        return create_engine(config)

    def init_db(self):
        """创建传输工具所需要的基础表"""
        engine = self.get_orm_engine()
        Base.metadata.create_all(engine)

    def init_table(self):
        """往传输工具表中写入基础数据"""
        engine = self.get_orm_engine()

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
        self._config = Config()

    def get_orm_engine(self, engine_name=None):
        """获取orm引擎"""
        config = self._config.get_orm_engine(engine_name)
        return create_engine(config)

    def get_orm_session(self,engine_name=None):
        engine = self.get_orm_engine(engine_name)
        session = sessionmaker(bind=engine)()
        return session

    def get_trans_list(self):
        """获取传输接口"""
        session = self.get_orm_session()
        return session.query(TransType).all()

    def set_trans_list(self, transtype_list):
        """更新传输接口"""
        session = self.get_orm_session()
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
        return True

    def get_trans_log(self, *args, **kwargs):
        """获取传输日志列表"""
        session = self.get_orm_session()
        result = session.query(TransLog)
        if kwargs.get("no", None):
            result = result.filter(TransLog.no.like('{}%'.format(kwargs["no"])))
        if kwargs.get("begin_time",None):
            result = result.filter(TransLog.begin_time >= kwargs["begin_time"])
        if kwargs.get("end_time", None):
            result = result.filter(TransLog.end_time <= kwargs["end_time"])
        if kwargs.get("status", ''):
            result = result.filter(TransLog.status == kwargs["status"])

        return result.all()


if __name__ == "__main__":
    # provider = TransDataProvider()
    # print(provider.get_trans_log(status="1", begin_time="2018-09-12"))
    provider = TransDataProvider()
    print(provider.get_trans_log())


