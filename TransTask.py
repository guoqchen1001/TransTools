import time, datetime
from sqlalchemy import Table, MetaData,Column, String
from sqlalchemy.sql import text
from TransModels import WMSTable
from TransDataProvider import TransDataProvider


class SourceDataNotDefined(Exception):

    def __str__(self):
        return "传输任务数据来源没有定义"


class TargetTableNotDefined(Exception):

    def __str__(self):
        return "传输任务目的数据模型没有定义"


class UpdateSourceFlagError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "更新源数据更新表示出错,错误信息:{}".format(self.msg)


class InsertTargetFlagError(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "写入数据到目的数据库时出错,错误信息:{}".format(self.msg)


class TransTask:

    _provider = TransDataProvider()

    source_engine_name = None  # 来源数据库
    target_engine_name = None  # 目标数据库

    _source_metadata = None  # 来源数据库连接
    _source_engine = None  # 来源数据库metadata

    select_data = None  # 待处理数据

    target_table = None  # 写入数据模型
    source_table = None  # 源数据模型

    sql = None  # 获取数据sql,如果定义了来源数据模型，则以来源数据模型来取数据
    update_flag_table = None
    update_target_col_name = None
    update_source_col_name = None

    update_clause = dict(ftrans_wms_flag=1)
    update_tmptable = None

    def get_from_source(self):
        """从源数据获取数据"""
        if self.source_table is None and  self.sql is None:
            raise SourceDataNotDefined
        if self.source_table is not None:
            return False
        else:
            return self.get_data_from_sql(self.sql)

    def upert_to_target(self):
        """写入数据"""
        if self.target_table is None:
            raise TargetTableNotDefined
        return self.upert_data_to_basetable()

    def update_flag_to_source(self):
        """更新原状态"""
        engine = self._source_engine
        metadata = MetaData(bind=engine)
        conn = engine.connect()
        timestap = int(round(time.time()*1000))
        temptable_name = "#{}{}".format(self.__class__.__name__, timestap)

        # 创建临时表
        self.update_tmptable = Table(temptable_name, metadata,
                          Column(self.update_target_col_name, String(50), primary_key=True),
                          )

        # 必须绑定到此次链接，否则查询不到临时表
        self.update_tmptable.create(bind=conn)

        conn.execute(self.update_tmptable.insert(), self.select_data)
        tran = conn.begin()
        stmt = self.update_flag_table.update()\
            .where(self.update_flag_table.c[self.update_source_col_name] == self.update_tmptable.c[self.update_target_col_name])\
            .values(**self.update_clause)
        try:
            conn.execute(stmt)
            tran.commit()
            return True
        except Exception as e:
            tran.rollback()
            raise UpdateSourceFlagError(str(e))
        finally:
            conn.close()

    def get_engine(self, engine_name):
        """获取数据库引擎"""
        return self._provider.get_orm_engine(engine_name)

    def get_data_from_sql(self, sql):
        """通过sql获取数据"""
        engine = self.get_engine(self.source_engine_name)
        self._source_metadata = MetaData(bind=engine)
        self._source_engine = engine

        conn = engine.connect()
        self.select_data = conn.execute(sql).fetchall()
        conn.close()
        return True

    def upert_data_to_basetable(self):
        if not self.select_data:
            return
        engine = self.get_engine(self.target_engine_name)
        conn = engine.connect()
        trans = conn.begin()
        try:
            conn.execute(self.target_table.insert(), self.select_data)
            self.update_flag_to_source()
            trans.commit()
            return True
        except Exception as e:
            trans.rollback()
            raise InsertTargetFlagError(str(e))
        finally:
            conn.close()

    def get_result(self):
        return len(self.select_data)

    @staticmethod
    def clone_table(name, table, metadata):
        """复制表结构"""
        cols = [c.copy() for c in table.columns]
        constraints = [c.copy() for c in table.constraints]
        return Table(name, metadata, *(cols + constraints))

    def run(self):
        # 读取数据

        # 获取数据
        self.get_from_source()

        # 写入数据
        self.upert_to_target()

        # 返回结果
        return self.get_result()


class ItemCls(TransTask):

    source_engine_name = "mssql"
    target_engine_name = "oracle"
    target_table = WMSTable.itemcls
    update_target_col_name = "GROUP_NO"
    update_source_col_name = "fitem_clsno"
    update_flag_table = Table(
            "t_bc_master", MetaData(),
            Column("fitem_clsno", String, primary_key=True),
            Column("ftrans_wms_flag", String)
        )

    sql = text(
      "select top 2 fitem_clsno as GROUP_NO, "
      "fitem_clsname  as GROUP_NAME,"
      "flvl_num as LEVELID,"
      "convert(varchar(30), ftransid) as SHEETID,"
      "case fprt_no when '*' then fitem_clsno else fprt_no end as HEADGROUP_NO "
      "from  t_bc_master " 
      "where ftrans_wms_flag <> '1'"
      )



















