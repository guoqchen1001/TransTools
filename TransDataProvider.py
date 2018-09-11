import yaml
import os
import chardet
import codecs
import pymssql
from enum import Enum
import pymysql
from collections import OrderedDict


class Engine(Enum):
    """数据库引擎枚举类型"""
    oracle = 'oracle'
    mssql = 'mssql'
    mysql = 'mysql'
    sqlite = 'sqlite'


class TransDataProvider:
    """传输工具数据提供接口"""
    def __init__(self):
        self.config_path = 'TransTools.yaml'    # 配置文件名称
        self.databases = 'databases'             # 配置文件数据库节点名称
        self.default = 'default'                 # 配置文件默认节点名称
        self.proc = 'ts_pr_sys_trans'           # 数据库存储过程
        self.proc_log = 'ts_pr_sys_trans_log'  # 数据库日志处理存储过程
        self.table = "ts_t_sys_funclist"        # 数据库传输表

    def get_config(self):
        """获取配置文件，并解析为python对象"""
        if not os.path.exists(self.config_path):
            return False, '配置文件{}不存在'.format(self.config_path)
        with open(self.config_path, 'rb') as f:
            encoding = chardet.detect(f.read())['encoding']
        with codecs.open(self.config_path, encoding=encoding) as f:
            try:
                y = yaml.load(f)
            except Exception as e:
                return False, "解析配置文件{}时发生异常:{}".format(self.config_path, str(e))
            return True, y

    def get_dbconnect(self, db):
        """获取数据库连接"""
        result, config = self.get_config()
        if not result:
            return result, config
        if self.databases not in config.keys():
            return False,"配置文件{}中不存在节点{}".format(self.config_path, self.databases)
        dbsettings = config[self.databases]
        if db not in dbsettings.keys():
            return False, "配置文件{}中{}节点不存在{}".format(self.config_path, self.databases, db)
        return True, dbsettings[db]

    def get_conn(self, dbname=None):
        """获取数据库连接对象"""

        # 数据库默认为默认数据库
        if dbname is None:
            dbname = self.default

        # 获取配置文件数据库链接信息
        result, dbsetting = self.get_dbconnect(dbname)
        if not result:
            return False, "获取数据连接失败，{}".format(dbsetting)
        try:
            if dbsetting['engine'] == Engine.mssql.value:
                conn = pymssql.connect(host=dbsetting['host'], user=dbsetting['user'], password=dbsetting['pwd'], database=dbsetting['db'])
                return True, conn
            elif dbsetting['engine'] == Engine.mysql.value:
                conn = pymysql.connect(host=dbsetting['host'], user=dbsetting['user'], password=dbsetting['pwd'], database=dbsetting['db'],
                                       cursorclass=pymysql.cursors.DictCursor)
                return True, conn
            else:
                return False, "不支持的数据库引擎{}".format(dbsetting)
        except Exception as e:
            return False, "数据库连接发生异常,错误信息：{}".format(str(e))

    def executesql(self, sql, parm=None, db=None, commit=False):
        """通过sql语句获取数据"""
        # sql sql语句
        # parm 执行参数
        # db 数据库，默认取default数据库
        # commit 是否提交事务

        if db is None:
            db = self.default
        result, conn = self.get_conn(db)
        if not result:
            return result, conn
        cursor = conn.cursor()
        try:
            if parm is None:
                cursor.execute(sql)
            else:
                cursor.executemany(sql, parm)

            if commit:
                conn.commit()
                return True, None
            else:
                result = cursor.fetchall()
                return True, result

        except Exception as e:
            err_msg = "获取数据时发生错误，错误信息" + str(e)
            return False, err_msg
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_proc_param(parm):
        """拼装过程传输参数"""
        parm_dict = parm
        if isinstance(parm, str):
            parm_dict = {"transtype": parm}
        if not isinstance(parm_dict, dict):
            return False, "参数格式不合法，必须放为字典类型"
        result = '\t'.join(["{}={}".format(k, parm_dict[k]) for k in parm_dict])
        return True, ('.{arg:%s}' % result,)

    def executeproc(self, parm, proc=None, db=None, as_dict=True, as_submit=False):
        """从存储过程获取数据"""

        # 数据库默认为default
        if db is None:
            db = self.default
        # 存储过程默认调用 zb_pr_crm_trans
        if proc is None:
            proc = self.proc
        # 存储过程如果只有一个参数，则转换为元组
        result, parm_sql = self.get_proc_param(parm)
        if not result:
            return result, parm_sql
        # 获取数据库连接
        result, conn = self.get_conn(db)
        if not result:
            return result, conn
        try:
            cursor = conn.cursor(as_dict=as_dict)
            cursor.callproc(proc, parm_sql)
            data = [row for row in cursor]
            if as_submit:
                conn.commit()
            conn.close()
            return True, data
        except Exception as e:
            return False, "{}获取数据发生错误:{}".format(parm, repr(e))
        finally:
            conn.close()

    def get_trans_list(self):
        """获取传输接口"""
        return self.executeproc('translist')

    def get_tran_data(self, transtype):
        """获取传输数据"""
        return self.executeproc(transtype, as_dict=False)

    def get_trans_log(self, *args, **kwargs):
        """获取传输日志列表"""
        parm = kwargs
        parm['transtype'] = 'log'
        return self.executeproc(parm)

    def set_trans_opertime(self, *args, **kwargs):
        """设置最后一次运行时间"""
        parm = kwargs
        parm['opertype'] = 'opertime'
        return self.executeproc(parm, self.proc_log, as_submit=True)

    def set_trans_operinfo(self, *args, **kwargs):
        """设置结果日志"""
        parm = kwargs
        parm["opertype"] = "operinfo"
        return self.executeproc(parm, self.proc_log, as_submit=True)

    def update(self, data, table=None, pk=None):
        """更新数据"""
        if not data:
            return True, "无数据更新"
        if not data[0]:
            return True, "无数据更新"

        data_ordered = [OrderedDict(row.items()) for row in data]
        data_list_sum = []
        flag = True
        col_list = []
        pk_col_list = []
        for row in data_ordered:
            data_list = []
            pk_list = []
            for key in row.keys():
                if key not in pk:
                    data_list.append(row[key])
                    if flag:
                        col_list.append(key)
                else:
                    pk_list.append(row[key])
                    if flag:
                        pk_col_list.append(key)
            flag = False
            data_list = data_list + pk_list
            data_list_sum.append(tuple(data_list))

        _set = ','.join(["{}=%s".format(col) for col in col_list])
        _where = ' and '.join(["{}=%s".format(col) for col in pk_col_list])
        sql = " update {} set {} where {}".format(self.table, _set, _where)
        return self.executesql(sql, parm=data_list_sum, commit=True)

    def update_setting(self, data):
        return self.update(data, table=self.table, pk="fsheetid")






