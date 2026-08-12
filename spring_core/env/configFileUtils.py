import abc

import yaml


class BaseConfigReader:
    def __init__(self, file_name):
        self.file_name = file_name

    @abc.abstractmethod
    def getProperties(self, encoding="utf-8"):
        pass


# 读取Properties文件类
class PropertiesReader(BaseConfigReader):
    """
    读取 .properties 文件
    """
    def getProperties(self, encoding="utf-8"):
        data = {}
        try:
            pro_file = open(self.file_name, 'r', encoding=encoding)
            for line in pro_file:
                if not line.startswith("#") and line.find('=') > 0:
                    strs = line.replace('\n', '').split('=')
                    data[strs[0]] = strs[1]
        except Exception as e:
            raise e
        else:
            pro_file.close()
        return data


class YamlReader(BaseConfigReader):
    """
    读取 .yaml 文件
    """
    def getProperties(self, encoding="utf-8"):
        data = {}
        # 读取YAML文件
        with open(self.file_name, "r", encoding=encoding) as file:
            data = yaml.safe_load(file)

        # 访问YAML文件中的数据
        return data


def test_read_properties():
    file_path = '../../config/application.properties'
    # 声明一个Properties类的实例，调用其getProperties方法，返回一个字典
    result = PropertiesReader(file_path).getProperties("gbk")
    print(result)


def test_read_yaml():
    file_path = '../../config/application-test.yaml'
    result = YamlReader(file_path).getProperties()
    print(result)


if __name__ == '__main__':
    test_read_properties()
    test_read_yaml()
