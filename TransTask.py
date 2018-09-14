import time
from sqlalchemy import Table, MetaData,Column, String
from sqlalchemy.sql import text
from TransModels import WMSTable
from TransDataProvider import TransDataProvider

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
        if self.source_table:
            return False, None
        else:
            if self.sql is not None:
                return self.get_data_from_sql(self.sql)
            else:
                return False, "请定义有效的来源数据模型或者sql"

    def upert_to_target(self):
        """写入数据"""
        if self.target_table is None:
            return False, "请定义有效的来源数据模型"
        return self.upert_data_to_basetable()

    def update_flag_to_source(self):
        """更新原状态"""
        engine = self._source_engine
        metadata = MetaData(bind=engine)
        conn = engine.connect()
        now = int(round(time.time()*1000))
        temptable_name = "#{}{}".format(self.__class__.__name__, now)
        # 创建临时表
        self.update_tmptable = Table(temptable_name, metadata,
                          Column(self.update_target_col_name, String(50), primary_key=True),
                          )
        # 必须绑定到此次链接，否则查询不到临时表
        self.update_tmptable.create(bind=conn)
        conn.execute(self.update_tmptable.insert(), self.select_data)
        stmt = self.update_flag_table.update()\
            .where(self.update_flag_table.c[self.update_source_col_name] == self.update_tmptable.c[self.update_target_col_name])\
            .values(**self.update_clause)
        tran = conn.begin()

        try:
            conn.execute(stmt)
            tran.commit()
            return True, None
        except Exception as e:
            tran.rollback()
            return False, "更新写入标志出错,错误信息{}".format(str(e))
        finally:
            conn.close()

    def get_engine(self, engine_name):
        """获取数据库引擎"""
        return self._provider.get_orm_engine(engine_name)

    def get_data_from_sql(self, sql):
        """通过sql获取数据"""
        result, engine = self.get_engine(self.source_engine_name)
        if not result:
            return result, engine
        self._source_metadata = MetaData(bind=engine)
        self._source_engine = engine
        try:
            conn = engine.connect()
            self.select_data = conn.execute(sql).fetchall()
            conn.close()
            return True, None
        except Exception as e:
            return False, str(e)

    def upert_data_to_basetable(self):
        if not self.select_data:
            return True, None
        result, engine = self.get_engine(self.target_engine_name)
        if not result:
            return result, engine
        conn = engine.connect()
        trans = conn.begin()
        try:
            conn.execute(self.target_table.insert(), self.select_data)
            result, data = self.update_flag_to_source()
            if not result:
                trans.rollback()
                return False, "更新数据库标识时出现异常，错误信息：{}".format(data)
            else:
                trans.commit()
                return True, None
        except Exception as e:
            trans.rollback()
            return False, "写入数据库导数据时发生异常，错误信息:{}".format(str(e))
        finally:
            conn.close()

    @staticmethod
    def clone_table(name, table, metadata):
        """复制表结构"""
        cols = [c.copy() for c in table.columns]
        constraints = [c.copy() for c in table.constraints]
        return Table(name, metadata, *(cols + constraints))

    def run(self):
        # 读取数据
        result, data = self.get_from_source()
        if not result:
            return result, data
        # 写入数据
        result, data = self.upert_to_target()
        if not result:
            return result, data
        return True, len(self.select_data)


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
      "select fitem_clsno as GROUP_NO, "
      "fitem_clsname  as GROUP_NAME,"
      "flvl_num as LEVELID,"
      "convert(varchar(30), ftransid) as SHEETID,"
      "case fprt_no when '*' then fitem_clsno else fprt_no end as HEADGROUP_NO "
      "from  t_bc_master " 
      "where ftrans_wms_flag <> '1'"
      ).columns(
        WMSTable.itemcls.c.GROUP_NO,
        WMSTable.itemcls.c.GROUP_NAME,
        WMSTable.itemcls.c.LEVELID,
        WMSTable.itemcls.c.SHEETID,
        WMSTable.itemcls.c.HEADGROUP_NO
    )



itemcls = ItemCls()
itemcls.get_from_source()
print(itemcls.run())









