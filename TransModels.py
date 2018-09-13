from sqlalchemy import Column, String, Integer, DateTime, NVARCHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TransType(Base):
    """传输"""
    __tablename__ = 'ts_t_sys_funclist'
    no = Column(String(25), primary_key=True, nullable=False, default="", comment="传输编码")
    prtno = Column(String(25), nullable=False, default='', comment="父级编码")
    lvl = Column(Integer, nullable=False, default=0, comment="级别")
    srlid = Column(Integer, nullable=False, default=0, comment="序号")
    text = Column(NVARCHAR(50), nullable=False, default='', comment="名称")
    sheetid = Column(String(20), nullable=False, default='', comment="接口id")
    status = Column(String(1), nullable=False, default='', comment="状态 0/终止 1 正常")
    space_type = Column(String(1), nullable=False, default='', comment="间隔类型 0/小时 1/分钟")
    space_time = Column(Integer, nullable=False, default=0, comment="间隔时间")
    start_hour = Column(Integer, nullable=False, default=0, comment="开始小时数，范围0-23")
    end_hour = Column(Integer, nullable=False, default=0, comment="结束小时数, 范围0-23")
    trans_type = Column(String, nullable=False, default='', comment="传输类型(0/自动 1/手动")
    last_time = Column(DateTime, comment="最后一次传输时间")
    max_transid = Column(Integer, nullable=False, default=0, comment="最大transid")
    translog = relationship("TransLog", back_populates="transtype")

    def __repr__(self):
        return "<TransType {}>".format(self.no)


class TransLog(Base):
    """传输日志"""
    __tablename__ = "ts_t_sys_log"
    id = Column(Integer, ForeignKey("ts_t_sys_funclist.no"), primary_key=True,autoincrement=True)
    no = Column(String(25), nullable=False, default="", comment="传输编码")
    status = Column(String, comment="传输状态")
    begin_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结算时间")
    trans_count = Column(Integer, comment="传输时间")
    msg = Column(NVARCHAR, comment="错误信息")
    transtype = relationship("TransType")

    def __repr__(self):
        return "<TransLog {}>".format(self.id)



def get_init_translist():
    """获取基础传输信息"""
    # 一级
    wms = TransType(no="wms", prtno="*", lvl=1, srlid=1, text="wms数据传输中心")

    # 二级
    base = TransType(no="wms.base", prtno="wms", lvl=2, srlid=1, text="基础资料")
    sheet = TransType(no="wms.sheet", prtno="wms", lvl=2, srlid=2, text="业务单据")

    # 三级
    item = TransType(no="wms.base.item", prtno="wms.base", lvl=3, srlid=1, text="商品信息", sheetid="item")
    itemcls = TransType(no="wms.base.itemcls", prtno="wms.base", lvl=3, srlid=2, text="商品类别", sheetid="itemcls")
    barcode = TransType(no="wms.base.barcode", prtno="wms.base", lvl=3, srlid=3, text="多包装", sheetid="barcode")
    order = TransType(no="wms.sheet.order", prtno="wms.sheet", lvl=3, srlid=1, text="采购订单", sheetid="order")
    returnorder = TransType(no="wms.sheet.returnorder", prtno="wms.sheet", lvl=3, srlid=2, text="采购退货单",sheetid="returnorder")

    return wms, base, sheet, item, itemcls, barcode, order, returnorder

