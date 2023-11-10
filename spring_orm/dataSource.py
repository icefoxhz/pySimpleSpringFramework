# -*- coding: utf-8 -*-
import threading
import urllib.parse
from queue import Queue

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

from pySimpleSpringFramework.spring_pdbc.pdbc import PyDatabaseConnectivity

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
        self._ds_name = ds_name
        self._url = url
        self._username = username
        self._password = password
        self._pool_size = pool_size
        self._pool_recycle = pool_recycle
        self._max_overflow = max_overflow
        self._pool_timeout = pool_timeout
        self._engine = None

        self._after_init()

    def __get_dataSource_threadLocal(self):
        if not hasattr(self.__local_obj, "dstl"):
            self.__local_obj.dstl = DataSourceThreadLocal()
        return self.__local_obj.dstl

    def __get_dataSource_threadLocal_queue(self):
        if not hasattr(self.__local_obj, "dstl_queue"):
            self.__local_obj.dstl_queue = Queue(maxsize=20)
        return self.__local_obj.dstl_queue

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
        if self.is_new:
            q = self.__get_dataSource_threadLocal_queue()
            q.put(dstl)
            self.__local_obj.dstl = DataSourceThreadLocal()
            dstl = self.__local_obj.dstl
            dstl.is_new = True

        session = dstl.current_session \
            if dstl.current_session is not None else self.__get_session_from_thread_local()
        # print(dstl.current_session)
        return session

    def set_autocommit(self, autocommit=True):
        dstl = self.__get_dataSource_threadLocal()
        dstl.autocommit = autocommit

    def __parse_to_real_url(self):
        """
        处理密码中的特殊字符。比如 @
        :return:
        """
        password = self._password
        encoded_password = urllib.parse.quote(password)
        user_ps = f"{self._username}:{encoded_password}@"
        ls = self._url.split("//")
        self._url = ls[0] + "//" + user_ps + ls[1]
        # print(self._url)

    def _after_init(self):
        self.__parse_to_real_url()

        # 新版本默认 autocommit是False， 且无法手动设置为True
        self._engine = create_engine(
            url=self._url,
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
            dstl.current_session = scoped_session(self.__session_factory)
        return dstl.current_session

    def raw_query(self, sql) -> object or None:
        session = self.get_session()
        ex = None
        try:
            return session.execute(text(sql))
        except Exception as e:
            # log.error("raw_query => " + str(e))
            ex = e
        finally:
            self.raw_close()

            if ex is not None:
                raise ex

        return None

    def query_to_df(self, sql) -> pd.DataFrame or None:
        return pd.read_sql_query(sql, self._engine)

    def raw_execute(self, *sqls):
        dstl = self.__get_dataSource_threadLocal()
        autocommit = dstl.autocommit
        session = self.get_session()
        # print("session = ", session)
        results = []
        ex = None
        try:
            for sql in sqls:
                result = session.execute(text(sql))
                results.append(result.rowcount)
                if autocommit:
                    session.commit()
        except Exception as e:
            ex = e
            self.raw_rollback()
        finally:
            if autocommit:
                self.raw_close()

            if ex is not None:
                raise ex

        return results if len(results) > 1 else results[0]

    def raw_commit(self):
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_session is not None:
            dstl.current_session.commit()

    def raw_rollback(self):
        dstl = self.__get_dataSource_threadLocal()
        if dstl.current_session is not None:
            dstl.current_session.rollback()

    def raw_close(self):
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
            self.__local_obj.dstl = q.get()
            self.__local_obj.is_new = self.__local_obj.dstl.is_new

    def shutdown(self):
        self._engine.dispose()


# if __name__ == '__main__':
#     ds = DataSource(ds_name="ds", url="mysql+pymysql://47.102.114.87:3306/test", username="root",
#                     password="112233QQwwee")
#     ds.new_session()
#     ds.set_autocommit(False)
#     ds.raw_execute("insert into t1(f1, f2) value('zs', '26')", "insert into t1(f1, f2) value('ls', '12')")
#
#     try:
#         ds.new_session()
#         ds.set_autocommit(False)
#         ds.raw_execute("insert into t1(f1, f21) value('ww', '54')")
#         ds.commit()
#     except:
#         pass
#     finally:
#         ds.recover_dstl()
#
#     ds.new_session()
#     ds.set_autocommit(False)
#     ds.raw_execute("insert into t1(f1, f2) value('zl', '11')")
#     ds.commit()
#     ds.recover_dstl()
#
#     ds.commit()
#     ds.recover_dstl()
#     ds.close()
