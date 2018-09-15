from sqlalchemy import Column, String, Integer, DateTime, NVARCHAR, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import Table, MetaData


Base = declarative_base()


class TransType(Base):
    """传输"""
    __tablename__ = 'ts_t_sys_funclist'
    no = Column(String(25), primary_key=True, nullable=False, default="", comment="传输编码")
    prtno = Column(String(25), nullable=False, default='', comment="父级编码")
    lvl = Column(Integer, nullable=False, default=0, comment="级别")
    srlid = Column(Integer, nullable=False, default=0, comment="序号")
    text = Column(NVARCHAR(50), nullable=False, default='', comment="名称")
    sheetid = Column(String(20), default='', comment="接口id")
    status = Column(String(1) , default='', comment="状态 0/终止 1 正常")
    space_type = Column(String(1), default='0', comment="间隔类型 0/分钟 1/小时")
    space_time = Column(Integer,  default=0, comment="间隔时间")
    start_hour = Column(Integer, nullable=False, default=0, comment="开始小时数，范围0-23")
    end_hour = Column(Integer, nullable=False, default=0, comment="结束小时数, 范围0-23")
    trans_type = Column(String(1),  default='0', comment="传输类型(0/自动 1/手动")
    last_time = Column(DateTime, comment="最后一次传输时间")
    max_transid = Column(Integer, nullable=False, default=0, comment="最大transid")

    def __repr__(self):
        return "<TransType {}>".format(self.no)

    def is_should_run(self):
        # 必须手动传输
        if self.trans_type == '0':
            return False
        now = datetime.datetime.now()
        # 必须在开始时间内
        if now.hour > self.end_hour or now.hour < self.start_hour:
            return False
        # 必须超过时间间隔
        if self.last_time is not None:
            time_delta = now - self.last_time
            if self.space_type == '0' and time_delta.seconds < self.space_time*60:
                return False
            if self.space_type == '1' and time_delta.seconds < self.space_time*3600:
                return False
        return True


class TransLog(Base):
    """传输日志"""
    __tablename__ = "ts_t_sys_log"
    id = Column(Integer,  primary_key=True, autoincrement=True, comment="id，自增列")
    sheetid = Column(String(25), nullable=False, default="", comment="传输编码")
    status = Column(String(1), comment="传输状态")
    begin_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    trans_count = Column(Integer, comment="传输时间")
    msg = Column(NVARCHAR(1024), comment="错误信息")
    text = Column(NVARCHAR(50), comment="名称")
    no = Column(String(30), comment="编码")

    def __repr__(self):
        return "<TransLog {}>".format(self.id)


class WMSTable:
    metadata = MetaData()
    """商品类别"""
    itemcls = Table("ETW_ARTICLEGROUP", metadata,
              Column("SHEETID", String(20), nullable=False, primary_key=True),
              Column("OWNER_NO", String(10),default="001", nullable=False, primary_key=True),
              Column("GROUP_NO", String(20), nullable=False, primary_key=True),
              Column("GROUP_NAME", NVARCHAR(45), nullable=False),
              Column("LEVELID", Integer, nullable=False, ),
              Column("HEADGROUP_NO", String(20), nullable=False),
              Column("ENTERPRISE_NO", String(15),default="8888", nullable=False, primary_key=True),
    )


class TransModelInit:

    trans_status_choice = {
        "全部": " ",
        "失败": "0",
        "成功": "1"
    }

    def get_init_translist():
        """获取基础传输信息"""
        # 一级
        wms = TransType(no="wms", prtno="*", lvl=1, srlid=1, text="wms数据传输中心", sheetid='')

        # 二级
        base = TransType(no="wms.base", prtno="wms", lvl=2, srlid=1, text="基础资料", sheetid='')
        sheet = TransType(no="wms.sheet", prtno="wms", lvl=2, srlid=2, text="业务单据", sheetid='')

        # 三级
        item = TransType(no="wms.base.item", prtno="wms.base", lvl=3, srlid=1, text="商品信息", sheetid="Item")
        itemcls = TransType(no="wms.base.itemcls", prtno="wms.base", lvl=3, srlid=2, text="商品类别", sheetid="ItemCls")
        barcode = TransType(no="wms.base.barcode", prtno="wms.base", lvl=3, srlid=3, text="多包装", sheetid="Barcode")
        order = TransType(no="wms.sheet.order", prtno="wms.sheet", lvl=3, srlid=1, text="采购订单", sheetid="Order")
        returnorder = TransType(no="wms.sheet.returnorder", prtno="wms.sheet", lvl=3, srlid=2, text="采购退货单",sheetid="ReturnOrder")

        return wms, base, sheet, item, itemcls, barcode, order, returnorder


