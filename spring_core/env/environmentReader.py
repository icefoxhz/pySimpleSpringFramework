import errno
import os
import types

from pySimpleSpringFramework.spring_core.env.configFileUtils import PropertiesReader, YamlReader
from pySimpleSpringFramework.spring_core.log import log


class EnvironmentReader:
    def __init__(self, ):
        self.__current_directory = os.getcwd()

    def read(self, *config_directories):
        current_directory = os.getcwd()
        result_dict = {}
        try:
            for directory in config_directories:
                config_dir = os.path.abspath(os.path.join(current_directory, directory))
                merged_dict = self.__do_load_all_configs(config_dir)
                result_dict.update(merged_dict)
        except Exception as e:
            raise Exception("读取配置文件出错，配置文件必须utf8编码! error = ", str(e))
        # print(result_dict)
        return result_dict

    @staticmethod
    def __read_properties(config_dir, file_name, ret_dict, write_log=False):
        """
        读取properties文件
        :param config_dir:
        :param file_name:
        :param ret_dict:
        :param write_log:
        :return:
        """
        full_file_path = os.path.join(config_dir, file_name)
        if os.path.exists(full_file_path):
            if write_log:
                log.info("读取配置文件: " + full_file_path)
            result_dict = PropertiesReader(full_file_path).getProperties()
            # print(result_dict)
            ret_dict.update(result_dict)

    @staticmethod
    def __read_yaml(config_dir, find_file_name, ret_dict, write_log=False):
        """
        读取yaml文件
        :param config_dir:
        :param find_file_name:
        :param ret_dict:
        :param write_log:
        :return:
        """
        full_file_path = os.path.join(config_dir, find_file_name)
        if os.path.exists(full_file_path):
            if write_log:
                log.info("读取配置文件: " + full_file_path)
            result_dict = YamlReader(full_file_path).getProperties()
            # print(result_dict)
            ret_dict.update(result_dict)

    @staticmethod
    def __getConfigFromPy(filePath, silent=False):
        d = types.ModuleType("config")
        d.__file__ = filePath
        try:
            with open(filePath, mode="rb") as config_file:
                exec(compile(config_file.read(), filePath, "exec"), d.__dict__)
            exclude_keys = []
            for key, value in d.__dict__.items():
                if str(key).startswith("__") and str(key).endswith("__"):
                    exclude_keys.append(key)
            for key in exclude_keys:
                if key in d.__dict__.keys():
                    d.__dict__.pop(key)
        except IOError as e:
            if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
                return None
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise

        return d.__dict__

    @staticmethod
    def __read_py(config_dir, find_file_name, ret_dict, write_log=False):
        """
       读取py配置文件
       :param config_dir:
       :param find_file_name:
       :param ret_dict:
       :param write_log:
       :return:
       """
        full_file_path = os.path.join(config_dir, find_file_name)
        if os.path.exists(full_file_path):
            if write_log:
                log.info("读取配置文件: " + full_file_path)
            result_dict = EnvironmentReader.__getConfigFromPy(full_file_path)
            ret_dict.update(result_dict)

    @staticmethod
    def __do_load_all_configs(config_dir):
        """
        获取所有配置，合并到一起返回
        :param config_dir:
        :return:
        """
        merged_dict = {}

        # 先找标准配置application.properties
        find_file_name = "application.properties"
        EnvironmentReader.__read_properties(config_dir, find_file_name, merged_dict, True)

        # 看application.properties中有没有设置 配置的候选者
        candidate_flag = merged_dict.get("spring.profiles.include", None)

        # 有候选者
        if candidate_flag is not None:
            log.info("spring.profiles.include = " + candidate_flag)
            find_file_name = "application-{}.properties".format(candidate_flag)
            EnvironmentReader.__read_properties(config_dir, find_file_name, merged_dict, True)

            find_file_name = "application-{}.yaml".format(candidate_flag)
            EnvironmentReader.__read_yaml(config_dir, find_file_name, merged_dict, True)

            find_file_name = "application-{}.py".format(candidate_flag)
            EnvironmentReader.__read_py(config_dir, find_file_name, merged_dict, True)
        else:
            find_file_name = "application.yaml"
            EnvironmentReader.__read_yaml(config_dir, find_file_name, merged_dict, True)
        # print(merged_dict)
        return merged_dict


if __name__ == '__main__':
    environmentReader = EnvironmentReader()
    environment = environmentReader.read(r"D:\project\python\pySimpleSpringProject\2.0\config")
    print(environment)
