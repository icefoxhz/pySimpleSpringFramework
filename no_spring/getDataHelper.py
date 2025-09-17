import os

import pandas as pd
from pySimpleSpringFramework.spring_core.env.configFileUtils import PropertiesReader, YamlReader
from sqlalchemy import create_engine


class GetDataHelper:
    def __init__(self):
        print("dir: ", os.getcwd())
        self.__properties_file_path = "config/application.properties"
        self.__yaml_file_path = None
        # pd从postgresql数据库获取数据
        self.__engine = None

    def read_param(self):
        p = PropertiesReader(self.__properties_file_path).getProperties()
        yaml_flag = p['spring.profiles.include']
        self.__yaml_file_path = f"config/application-{yaml_flag}.yaml"

        y = YamlReader(self.__yaml_file_path).getProperties()
        # print(y)
        calculate_source_id = y['project']['calculate_source_id']
        # print(calculate_source_id)
        url = y['datasource']['sources'][calculate_source_id]['url']
        user = y['datasource']['sources'][calculate_source_id]['username']
        pw = y['datasource']['sources'][calculate_source_id]['password']
        connect_args = y['datasource']['sources'][calculate_source_id]['connect_args']
        """
        url: postgresql+psycopg2://192.168.101.152:5432/ncmining
        username: postgres
        password: postgres
        """
        url = f"{url}?user={user}&password={pw}"
        return url, connect_args

    def get_data(self, table_name: str):
        if self.__engine is None:
            url, connect_args = self.read_param()
            self.__engine = create_engine(url, connect_args=connect_args)
        data = pd.read_sql(f"select * from {table_name}", self.__engine)
        self.close()
        return data

    # 断开连接
    def close(self):
        if self.__engine is not None:
            self.__engine.dispose()
            self.__engine = None


if __name__ == '__main__':
    df = GetDataHelper().get_data('boston')
    print(df.head())
