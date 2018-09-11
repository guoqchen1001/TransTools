from sqlalchemy import Column, String


class Trans:
    __table_name__ = 'ts_t_sys_funclist'
    no = Column(String(30),primary_key=True)

