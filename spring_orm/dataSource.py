# -*- coding: utf-8 -*-
from __future__ import annotations

import datetime
import re
import threading
import urllib.parse
from copy import deepcopy
from queue import Queue

import pandas as pd
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.types import NullType
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import (
    Integer, BigInteger, SmallInteger, Numeric, Float, Date, DateTime, Double, DOUBLE_PRECISION, VARCHAR, CHAR,
    String, Text, Boolean, LargeBinary, Time, Interval, JSON, ARRAY
)
from sqlalchemy.engine import reflection
from sqlalchemy.schema import CreateTable

try:
    import geoalchemy2  # ✅关键, 正确支持Geometry类型
except ImportError:
    print("geoalchemy2未安装，无法支持Geometry类型")

from pySimpleSpringFramework.spring_core.log import log
from pySimpleSpringFramework.spring_pdbc.pdbc import PyDatabaseConnectivity
from pySimpleSpringFramework.spring_orm.transferMeaningSymbol import transfer_meaning

_sqlalchemy_to_postgresql = {
    Integer: "INT",
    BigInteger: "INT",
    SmallInteger: "INT",
    Numeric: "FLOAT",
    Float: "FLOAT",
    Double: "FLOAT",
    Date: "DATE",
    DateTime: "TIMESTAMP",
    String: "VARCHAR",
    Text: "TEXT",
    Boolean: "BOOLEAN",
    LargeBinary: "BYTEA",
    Time: "TIME",
    DOUBLE_PRECISION: "FLOAT",
    VARCHAR: "VARCHAR"
}

_sqlalchemy_to_oracle = {
    Integer: "INT",
    BigInteger: "INT",
    SmallInteger: "INT",
    Numeric: "FLOAT",
    Double: "FLOAT",
    Float: "FLOAT",
    Date: "DATE",
    DateTime: "TIMESTAMP",
    String: "VARCHAR2",
    Text: "CLOB",
    Time: "TIMESTAMP",
    CHAR: "CHAR"
}

"""
https://www.baidu.com/link?url=vbyAdTFH8QPbTw5kU8XpBi75FNjI1wsrrqf3ilQq4F0iqAV4YpMorgC5d84MzKGuObZ0h1gvpanvOYEripokz_&wd=&eqid=ea690b56000b0cbd000000045e4615ec

create_engine() 函数和连接池相关的参数有：

-pool_recycle, 默认为 -1, 推荐设置为 7200, 即如果 connection 空闲了 7200 秒，自动重新获取，以防止 connection 被 db server 关闭。
-pool_size=5, 连接数大小，默认为 5，正式环境该数值太小，需根据实际情况调大
-max_overflow=10, 超出 pool_size 后可允许的最大连接数，默认为 10, 这 10 个连接在使用过后，不放在 pool 中，而是被真正关闭的。
-pool_timeout=30, 获取连接的超时阈值，默认为 30 秒
直接只用 create_engine 时，就会创建一个带连接池的引擎


如果还是经常断，参考
https://blog.csdn.net/weixin_30772105/article/details/98882352

"""


class DataSourceThreadLocal:
    def __init__(self):
        pass

    is_new = False
    autocommit = True
    current_session = None
    current_transaction = None
    current_conn = None

    def re_set(self):
        self.autocommit = True
        self.current_session = None
        self.current_transaction = None
        self.current_conn = None


class DataSource(PyDatabaseConnectivity):
    __chunk_size = 1000
    __local_obj = threading.local()

    def __reduce__(self):
        return self.__class__, (self._ds_name,
                                self._url,
                                self._username,
                                self._password,
                                self._pool_size,
                                self._pool_recycle,
                                self._max_overflow,
                                self._connect_args,
                                self._pool_timeout
                                )

    def __init__(self,
                 ds_name,
                 url,
                 username,
                 password,
                 pool_size=10,
                 pool_recycle=600,
                 max_overflow=1000,
                 connect_args=None,
                 pool_timeout=30):

        self._connect_args = {} if connect_args is None else connect_args

        # # 手动解析执行 SET search_path
        # self._set_search_path_sql = None
        # if connect_args is not None and "options" in connect_args.keys():
        #     ls = connect_args["options"].split(" ")
        #     for v in ls:
        #         if str(v).lower().startswith("search_path"):
        #             search_path_str = (str(v).split("=")[1])
        #             self._set_search_path_sql = "SET search_path TO " + search_path_str

        self._ds_name = ds_name
        self._url = url
        self._username = username
        self._password = password
        self._pool_size = pool_size
        self._pool_recycle = pool_recycle
        self._max_overflow = max_overflow
        self._pool_timeout = pool_timeout
        self._engine = None
        self.__is_debug_sql = False

        self._after_init()

    def debug_sql(self, is_debug):
        self.__is_debug_sql = is_debug

    @staticmethod
    def _render_actual_sql(sql, params):
        """
        把 :name 占位符替换为字面值，仅用于 debug 打印，**不会真正执行**
        - str   → 'value' (单引号包裹，内部单引号转义)
        - None  → NULL
        - bool  → TRUE / FALSE
        - 数字  → 原值
        - 时间  → 'isoformat' 单引号包裹
        """
        if not params:
            return sql

        def _sub(match):
            key = match.group(1)
            if key not in params:
                return match.group(0)
            v = params[key]
            if v is None:
                return "NULL"
            if isinstance(v, bool):
                return "TRUE" if v else "FALSE"
            if isinstance(v, (int, float)):
                return str(v)
            if isinstance(v, (datetime.datetime, datetime.date)):
                return "'" + v.isoformat() + "'"
            return "'" + str(v).replace("'", "''") + "'"

        return re.sub(r"(?<!:):([A-Za-z_]\w*)", _sub, sql)

    def _print_sql(self, *sqls):
        if not self.__is_debug_sql:
            return
        for s in sqls:
            if isinstance(s, dict):
                actual = self._render_actual_sql(s.get('sql', ''), s.get('params') or {})
                log.debug(actual)
            else:
                log.debug(s)

    @staticmethod
    def _render_actual_sql(sql, params):
        """
        把 :name 占位符替换为字面值，仅用于 debug 打印，**不会真正执行**
        - str   → 'value' (单引号包裹，内部单引号转义)
        - None  → NULL
        - bool  → TRUE / FALSE
        - 数字  → 原值
        - 时间  → 'isoformat' 单引号包裹
        """
        if not params:
            return sql

        def _sub(match):
            key = match.group(1)
            if key not in params:
                return match.group(0)
            v = params[key]
            if v is None:
                return "NULL"
            if isinstance(v, bool):
                return "TRUE" if v else "FALSE"
            if isinstance(v, (int, float)):
                return str(v)
            if isinstance(v, (datetime.datetime, datetime.date)):
                return "'" + v.isoformat() + "'"
            return "'" + str(v).replace("'", "''") + "'"

        return re.sub(r"(?<!:):([A-Za-z_]\w*)", _sub, sql)

    def getTableFieldsMeta(self, table_name):
        fieldMapping = {}
        # 使用Inspector检查表结构
        inspector = inspect(self._engine)
        # 获取字段名及其类型
        for column in inspector.get_columns(table_name):
            # print(f"Column: {column['name']}, Type: {column['type']}")
            fieldMapping[column['name']] = column['type']

        return fieldMapping

    @staticmethod
    def get_field_mapping(sqlalchemy_field_type, sqlalchemy_to_db):
        for sqlalchemy_type, postgresql_type in sqlalchemy_to_db.items():
            if isinstance(sqlalchemy_field_type, sqlalchemy_type):
                return postgresql_type
        return None

    def getPostgresqlTableFieldsMeta(self, table_name):
        fieldMapping = {}
        # 使用Inspector检查表结构
        inspector = inspect(self._engine)
        # 获取字段名及其类型
        for column in inspector.get_columns(table_name):
            # print(f"Column: {column['name']}, Type: {column['type']}")
            # fieldMapping[column['name']] = column['type']
            sqlalchemy_field_type = column['type']
            postgresql_field_type = self.get_field_mapping(sqlalchemy_field_type, _sqlalchemy_to_postgresql)
            val = postgresql_field_type if postgresql_field_type else str(sqlalchemy_field_type)
            # if val is not None and val != "NULL":
            fieldMapping[column['name']] = val
        return fieldMapping

    def getOracleTableFieldsMeta(self, table_name):
        fieldMapping = {}
        # 使用Inspector检查表结构
        inspector = inspect(self._engine)
        # 获取字段名及其类型
        for column in inspector.get_columns(table_name):
            # print(f"Column: {column['name']}, Type: {column['type']}")
            # fieldMapping[column['name']] = column['type']
            sqlalchemy_field_type = column['type']
            postgresql_field_type = self.get_field_mapping(sqlalchemy_field_type, _sqlalchemy_to_oracle)
            val = postgresql_field_type if postgresql_field_type else str(sqlalchemy_field_type)
            # if val is not None and val != "NULL":
            fieldMapping[column['name']] = val
        return fieldMapping

    def __get_dataSource_threadLocal(self):
        if not hasattr(self.__local_obj, "dstl"):
            self.__local_obj.dstl = DataSourceThreadLocal()
        return self.__local_obj.dstl

    def __get_dataSource_threadLocal_queue(self):
        if not hasattr(self.__local_obj, "dstl_queue"):
            self.__local_obj.dstl_queue = Queue(maxsize=20)
        return self.__local_obj.dstl_queue

    def get_table_ddl(self, table_name):
        # inspector = reflection.Inspector.from_engine(self._engine)
        # # 获取主键
        # pk = inspector.get_pk_constraint(table_name)
        # # 获取外键（可选，若需要完全复制）
        # foreign_keys = inspector.get_foreign_keys(table_name)
        # # 获取索引
        # indexes = inspector.get_indexes(table_name)

        # 2. 构建 CREATE TABLE 语句
        # 使用 SQLAlchemy 的 Table 对象反射，再生成 DDL
        metadata = MetaData()
        src_reflected = Table(table_name, metadata, autoload_with=self._engine)

        return str(CreateTable(src_reflected))

    @property
    def engine(self):
        return self._engine

    @property
    def is_new(self):
        if not hasattr(self.__local_obj, "is_new"):
            self.__local_obj.is_new = False
        return self.__local_obj.is_new

    def get_ds_name(self):
        return self._ds_name

    def create_new_session(self):
        if hasattr(self.__local_obj, "dstl"):
            self.__local_obj.is_new = True

    def create_or_get_session(self):
        dstl = self.__get_dataSource_threadLocal()
        is_create = dstl.current_session is None
        self.get_session()
        return is_create

    def get_session(self):
        dstl = self.__get_dataSource_threadLocal()
        if self.is_new and dstl.current_session is None:
            q = self.__get_dataSource_threadLocal_queue()
            q.put(dstl)
            self.__local_obj.dstl = DataSourceThreadLocal()
            dstl = self.__local_obj.dstl
            dstl.is_new = True
            dstl.autocommit = False

        session = dstl.current_session \
            if dstl.current_session is not None else self.__get_session_from_thread_local()
        # print(dstl.current_session)

        return session

    def set_autocommit(self, autocommit=True):
        dstl = self.__get_dataSource_threadLocal()
        dstl.autocommit = autocommit

    @property
    def autocommit(self):
        dstl = self.__get_dataSource_threadLocal()
        return dstl.autocommit

    @staticmethod
    def _parse_to_real_url(url, username, password):
        """
        处理密码中的特殊字符。比如 @
        :return:
        """
        encoded_password = urllib.parse.quote(password)
        user_ps = f"{username}:{encoded_password}@"
        ls = url.split("//")
        url = str(ls[0]) + "//" + str(user_ps) + str(ls[1])
        return url

    def _after_init(self):
        # 新版本默认 autocommit是False， 且无法手动设置为True
        self._engine = create_engine(
            url=self._parse_to_real_url(self._url, self._username, self._password),
            pool_recycle=self._pool_recycle,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            pool_timeout=self._pool_timeout,
            connect_args=self._connect_args,
            pool_pre_ping=True,
        )

        # 创建DBSession类型:
        self.__session_factory = sessionmaker(bind=self._engine)

    def __get_engine(self) -> object:
        return self._engine

    def __get_transaction_from_thread_local(self, connection) -> object:
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_transaction is None:
            dstl.current_transaction = connection.begin()
        return dstl.current_transaction

    def __get_conn_from_thread_local(self) -> object:
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_conn is None:
            dstl.current_conn = self._engine.connect()
        return dstl.current_conn

    def __get_session_from_thread_local(self) -> scoped_session:
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_session is None:
            self.__local_obj.dstl.current_session = scoped_session(self.__session_factory)
        return dstl.current_session

    @staticmethod
    def _normalize_sql(sql, use_text):
        """
        统一 sql 入参格式：
        - use_text=True  : 返回 {"sql": "...", "params": {...}}
        - use_text=False : 返回纯字符串
        支持 str / dict 两种入参，避免 transfer_meaning 在 dict 上崩溃
        """
        # use_text=True
        if use_text:
            if isinstance(sql, str):
                return {"sql": transfer_meaning(sql), "params": {}}
            return sql
        # use_text=False
        if isinstance(sql, dict):
            return sql["sql"]
        return transfer_meaning(sql)

    def raw_query(self, sql: str or dict, use_text=True) -> object or None:
        self._print_sql(sql)

        session = self.get_session()
        ex = None
        try:
            normalized = self._normalize_sql(sql, use_text)
            if use_text:
                return session.execute(text(normalized["sql"]), normalized["params"])
            return session.execute(text(normalized))
        except Exception as e:
            # log.error("raw_query => " + str(e))
            ex = e
        finally:
            self.raw_close()

            if ex is not None:
                raise ex

        return None

    def query_to_df(self, sql: str or dict, use_text=True) -> pd.DataFrame or None:
        normalized = self._normalize_sql(sql, use_text)
        self._print_sql(normalized)
        if use_text:
            return pd.read_sql_query(text(normalized["sql"]), self._engine, params=normalized["params"])
        return pd.read_sql_query(normalized, self._engine)

    def query_table_to_df(self, table_name, columns: list[str] | None = None) -> pd.DataFrame or None:
        self._print_sql(f"query table: {table_name}, columns: {columns if columns is not None else '*'}")
        return pd.read_sql_table(table_name, self._engine, columns=columns)

    def raw_execute(self, *sqls : list[str] or list[dict], use_text=True):
        new_sqls = [self._normalize_sql(sql, use_text) for sql in sqls]
        self._print_sql(*new_sqls)

        dstl = self.__get_dataSource_threadLocal()
        autocommit = dstl.autocommit
        session = self.get_session()
        # print("session = ", session)
        results = []
        ex = None
        try:
            for sql in new_sqls:
                if use_text:
                    result = session.execute(text(sql["sql"]), sql["params"])
                else:
                    result = session.execute(text(sql))
                try:
                    # sql一般会以returning id结尾
                    results.append(result.scalar())
                except:
                    results.append(result.rowcount)
                if autocommit:
                    session.commit()
        except Exception as e:
            ex = e
            if autocommit:
                self.raw_rollback()
        finally:
            if autocommit:
                self.raw_close()

            if ex is not None:
                raise ex

        return results if len(results) > 1 else results[0]

    def raw_commit(self):
        self._print_sql("执行commit")
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_session is not None:
            dstl.current_session.commit()

    def raw_rollback(self):
        self._print_sql("执行rollback")
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_session is not None:
            dstl.current_session.rollback()

    def raw_close(self):
        # self._print_sql("关闭session")
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_session is not None:
            dstl.current_session.close()
            dstl.current_session = None

    def commit(self):
        self.raw_commit()

    def close(self):
        self.raw_close()
        self.__clear_local_thread()

    def __clear_local_thread(self):
        dstl = self.__get_dataSource_threadLocal()
        dstl.re_set()

    def rollback(self):
        self.raw_rollback()

    def recover_dstl(self):
        # dstl = self.__get_dataSource_threadLocal()
        if self.is_new:
            # del dstl
            q = self.__get_dataSource_threadLocal_queue()
            if not q.empty():
                self.__local_obj.dstl = q.get()
                self.__local_obj.is_new = self.__local_obj.dstl.is_new

    def execute_by_df(self, dataframe, table_name, if_exists='append', is_create_index=False) -> bool:
        self._print_sql(f"run execute_by_df(...), table_name: {table_name}, if_exists={if_exists}")

        dstl = self.__get_dataSource_threadLocal()
        autocommit = dstl.autocommit
        ex = None
        # 使用事务
        session = self.get_session()
        try:
            dataframe.to_sql(table_name, session.connection(),
                             if_exists=if_exists,
                             index=is_create_index,
                             chunksize=self.__chunk_size)

            if autocommit:
                session.commit()
            return True
        except Exception as e:
            if autocommit:
                session.rollback()
            ex = e
            log.error("execute_by_df ERROR: " + str(e))
        finally:
            if autocommit:
                self.raw_close()

            if ex is not None:
                raise ex

        return False

    def shutdown(self):
        self._print_sql("关闭数据库线程池")
        self._engine.dispose()

# if __name__ == '__main__':
#     import pickle
#
#     obj = DataSource("ds1", "postgresql+psycopg2://192.168.101.152:5432/test2", "postgres", "postgres")
#     df = obj.query_to_df("select * from \"Poyanglake_HYDPL_2024\"")
#     print(df)
#
#     # obj = DataSource("ds1", "mysql+pymysql://47.102.114.87:3306/hz_test", "root", "112233QQwwee")
#     # serialized_data = pickle.dumps(obj)
#     # print(serialized_data)
#     # # Perform the deserialization if needed
#     # deserialized_obj = pickle.loads(serialized_data)
#     # print(deserialized_obj)
#     #
#     # ds = DataSource(ds_name="ds", url="mysql+pymysql://47.102.114.87:3306/test", username="root",
#     #                 password="112233QQwwee")
#     # ds.new_session()
#     # ds.set_autocommit(False)
#     # ds.raw_execute("insert into t1(f1, f2) value('zs', '26')", "insert into t1(f1, f2) value('ls', '12')")
#     #
#     # try:
#     #     ds.new_session()
#     #     ds.set_autocommit(False)
#     #     ds.raw_execute("insert into t1(f1, f21) value('ww', '54')")
#     #     ds.commit()
#     # except:
#     #     pass
#     # finally:
#     #     ds.recover_dstl()
#     #
#     # ds.new_session()
#     # ds.set_autocommit(False)
#     # ds.raw_execute("insert into t1(f1, f2) value('zl', '11')")
#     # ds.commit()
#     # ds.recover_dstl()
#     #
#     # ds.commit()
#     # ds.recover_dstl()
#     # ds.close()
