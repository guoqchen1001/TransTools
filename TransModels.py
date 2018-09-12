from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()
Session = scoped_session(sessionmaker())
engine = None


class TransType(Base):
    """传输"""
    __tablename__ = 'ts_t_sys_funclist'
    no = Column(String(25), primary_key=True, nullable=False, default="", comment="传输编码")
    prtno = Column(String(25), nullable=False, default='', comment="父级编码")
    lvl = Column(Integer, nullable=False, default=0, comment="级别")
    srlid = Column(Integer, nullable=False, default=0, comment="序号")
    text = Column(String(50), nullable=False, default='', comment="名称")
    sheetid = Column(String(20), nullable=False, default='', comment="接口id")
    status = Column(String(1), nullable=False, default='', comment="状态 0/终止 1 正常")
    space_type = Column(String(1), nullable=False, default='', comment="间隔类型 0/小时 1/分钟")
    space_time = Column(Integer, nullable=False, default=0, comment="间隔时间")
    start_hour = Column(Integer, nullable=False, default=0, comment="开始小时数，范围0-23")
    end_hour = Column(Integer, nullable=False, default=0, comment="结束小时数, 范围0-23")
    trans_type = Column(String, nullable=False, default='', comment="传输类型(0/自动 1/手动")
    last_time = Column(DateTime, comment="最后一次传输时间")
    max_transid = Column(Integer, nullable=False, default=0, comment="最大transid")




