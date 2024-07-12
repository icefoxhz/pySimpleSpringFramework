# -*- coding: utf-8 -*-
from __future__ import annotations

import threading
import time

import pandas as pd
from sqlalchemy.orm import scoped_session
from pySimpleSpringFramework.spring_core.log import log
from pySimpleSpringFramework.spring_orm.dataSource import DataSource


class DatabaseManager:
    __local_obj = threading.local()

    def __init__(self):
        self.__is_debug_sql = False
        self.__app_environment = None
        self.__datasource_map = {}
        self.__first_datasource = None
        self.__password_decrypter = None
        self.__db_type_dsNames = {
            "mysql": [],
            "oracle": [],
            "postgresql": []
        }
        self.__dsNameType = {}

    def start_debug(self):
        self.__local_obj.debug = True

    def debug_sql(self, is_debug):
        self.__is_debug_sql = is_debug

    def __before_do_sql(self, sql=None):
        if hasattr(self.__local_obj, "debug") and getattr(self.__local_obj, "debug"):
            setattr(self.__local_obj, "start_time", time.time())

    def __after_do_sql(self, sql=None):
        if hasattr(self.__local_obj, "debug") and getattr(self.__local_obj, "debug"):
            end_time = time.time()
            start_time = getattr(self.__local_obj, "start_time")
            # 计算执行时间
            execution_time = (end_time - start_time) * 1000
            s = "数据库执行耗时: {} 毫秒\nsql: {}".format(execution_time, sql if sql is not None else "dataframe")
            if execution_time > 500:
                log.warning(s)
            else:
                log.debug(s)

    def set_environment(self, applicationEnvironment):
        self.__app_environment = applicationEnvironment
        is_debug = self.__app_environment.get("datasource.debug_sql", False)
        is_debug = False if is_debug is None else is_debug
        self.debug_sql(is_debug)

    def set_password_decoder(self, passwordDecrypter):
        self.__password_decrypter = passwordDecrypter
        # print("passwordDecoder => ", self.__password_decrypter)
        if passwordDecrypter is not None:
            log.info("找到passwordDecoder: " + self.__password_decrypter.__class__.__name__)

    def after_init(self):
        self.__create_datasource()

    def __create_datasource(self):
        # 解析配置获取数据源
        datasource = self.__app_environment.get("datasource.sources", False)
        if datasource is None:
            return

        is_first = True
        for ds_name, ds_info in datasource.items():
            ds_name = str(ds_name)
            url = ds_info.get("url", None)
            username = ds_info.get("username", None)
            password = ds_info.get("password", None)
            if url is None or username is None or password is None:
                log.error("数据源: {} , 请设置 url、username、 password".format(ds_name))
                continue

            if self.__password_decrypter is not None:
                password = self.__password_decrypter.decrypt(password)
            # print("password => ", password)

            pool_size = 10
            pool_recycle = 600
            max_overflow = 1000
            connect_args = {}
            pool_timeout = 30
            pool_info = ds_info.get("pool", None)
            if pool_info is not None:
                pool_size = ds_info.get("size", pool_size)
                pool_recycle = ds_info.get("recycle", pool_recycle)
                max_overflow = ds_info.get("max_overflow", max_overflow)
                pool_timeout = ds_info.get("timeout", pool_timeout)
                connect_args = ds_info.get("connect_args", connect_args)

            ds = DataSource(ds_name=ds_name,
                            url=url,
                            username=username,
                            password=password,
                            pool_size=pool_size,
                            pool_recycle=pool_recycle,
                            max_overflow=max_overflow,
                            connect_args=connect_args,
                            pool_timeout=pool_timeout
                            )
            ds.debug_sql(self.__is_debug_sql)
            self.__datasource_map[ds_name] = ds
            if is_first:
                self.__first_datasource = ds
                is_first = False

            if str(url).lower().startswith("mysql"):
                self.__db_type_dsNames["mysql"].append(ds_name)
            if str(url).lower().startswith("oracle"):
                self.__db_type_dsNames["oracle"].append(ds_name)
            if str(url).lower().startswith("postgresql"):
                self.__db_type_dsNames["postgresql"].append(ds_name)

            J_SYMBOL = "+"
            db_type_name = "unKnow"
            if J_SYMBOL in url:
                db_type_name = str(url).split(J_SYMBOL)[0].lower()
            self.__dsNameType[ds_name] = db_type_name

            log.info("创建数据源成功: " + ds_name)

    def getTableFieldsMeta(self, table_name):
        try:
            ds = self.get_current_datasource()
            if ds is not None:
                return ds.getTableFieldsMeta(table_name)
        except Exception as e:
            log.error(str(e))
        return None

    def getPostgresqlTableFieldsMeta(self, table_name):
        try:
            ds = self.get_current_datasource()
            if ds is not None:
                return ds.getPostgresqlTableFieldsMeta(table_name)
        except Exception as e:
            log.error(str(e))
        return None

    def getOracleTableFieldsMeta(self, table_name):
        try:
            ds = self.get_current_datasource()
            if ds is not None:
                return ds.getOracleTableFieldsMeta(table_name)
        except Exception as e:
            log.error(str(e))
        return None

    def get_current_datasource(self) -> DataSource:
        ds = self.__local_obj.current_ds if hasattr(self.__local_obj,
                                                    "current_ds") and self.__local_obj.current_ds is not None else self.__first_datasource
        # print("current_datasource = ", ds)
        return ds

    def get_current_datasource_name(self) -> str:
        ds = self.get_current_datasource()
        return ds.get_ds_name() if ds is not None else None

    def get_current_datasource_type_name(self) -> str:
        ds_name = self.get_current_datasource_name()
        return self.__dsNameType.get(ds_name, "unKnow")

    def set_datasource_type_name(self, ds_name, type_name):
        self.__dsNameType[ds_name] = type_name

    def get_dsNames(self):
        return self.__db_type_dsNames

    def get_db_type(self, ds_name):
        ds_name = str(ds_name)
        for dbType, dsNames in self.__db_type_dsNames.items():
            if ds_name in dsNames:
                return dbType
        return None

    def get_session(self) -> scoped_session:
        ds = self.get_current_datasource()
        return ds.get_session()

    def create_new_session(self):
        ds = self.get_current_datasource()
        ds.create_new_session()

    def create_or_get_session(self):
        ds = self.get_current_datasource()
        return ds.create_or_get_session()

    def switch_datasource(self, name):
        name = str(name)
        if hasattr(self.__local_obj, "current_ds"):
            if self.__local_obj.current_ds is not None and self.__local_obj.current_ds.get_ds_name() == name:
                return

            if self.__local_obj.current_ds is not None:
                self.__local_obj.current_ds.close()

        switch_ds = self.__datasource_map.get(name, None)
        self.__local_obj.current_ds = switch_ds

    def set_autocommit(self, autocommit):
        ds = self.get_current_datasource()
        if ds is not None:
            ds.set_autocommit(autocommit)

    def raw_query(self, sql) -> object or None:
        try:
            self.__before_do_sql(sql)
            ds = self.get_current_datasource()
            if ds is not None:
                return ds.raw_query(sql)
            return None
        finally:
            self.__after_do_sql(sql)

    def query_to_df(self, sql) -> pd.DataFrame or None:
        if sql is None:
            return None

        try:
            self.__before_do_sql(sql)
            ds = self.get_current_datasource()
            if ds is not None:
                return ds.query_to_df(sql)
            return None
        finally:
            self.__after_do_sql(sql)

    def query_table_to_df(self, table_name, columns: list[str] | None = None) -> pd.DataFrame or None:
        if table_name is None:
            return None

        ds = self.get_current_datasource()
        if ds is not None:
            return ds.query_table_to_df(table_name, columns)
        return None

    def raw_execute(self, *sqls):
        if len(sqls) <= 0:
            return None

        results = None
        try:
            self.__before_do_sql(sqls)
            ds = self.get_current_datasource()
            if ds is not None:
                results = ds.raw_execute(*sqls)
        finally:
            self.__after_do_sql(sqls)
        return results

    def execute_by_df(self, dataframe, table_name, if_exists='append', is_create_index=False) -> bool:
        ds = self.get_current_datasource()
        if ds is None:
            return False
        return ds.execute_by_df(dataframe, table_name, if_exists, is_create_index)

    def recover_dstl(self):
        ds = self.get_current_datasource()
        if ds is not None:
            ds.recover_dstl()

    def commit(self):
        ds = self.get_current_datasource()
        if ds is not None:
            ds.commit()

    def close(self):
        ds = self.get_current_datasource()
        if ds is not None:
            ds.close()

    def rollback(self):
        ds = self.get_current_datasource()
        if ds is not None:
            ds.rollback()

    def shutdown(self):
        for ds in self.__datasource_map.keys():
            ds.shutdown()
        log.info("所有数据源关闭")

    @property
    def engine(self):
        ds = self.get_current_datasource()
        if ds is None:
            return False
        return ds.engine
