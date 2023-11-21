import os

from pySimpleSpringFramework.spring_beans.factory.support.defaultBeanFactory import DefaultBeanFactory
from pySimpleSpringFramework.spring_core.env.environmentReader import EnvironmentReader
from pySimpleSpringFramework.spring_core.log import log
from pySimpleSpringFramework.spring_core.util.scanner import Scanner


class SimpleApplicationContext:
    def __init__(self, debug=False):
        self.__debug = debug
        self.__current_directory = os.getcwd()
        self.config_directories = None
        self.base_packages = None
        self._environment = None
        self._bean_factory = None
        self._environmentReader = None
        self._scanner = None

        self.__after_init()

    def __after_init(self):
        self._bean_factory = DefaultBeanFactory()
        self._bean_factory.set_application_context(self)
        self._environmentReader = EnvironmentReader()
        self._scanner = Scanner(self._bean_factory)

    def register_singleton(self, bean_name, bean):
        self._bean_factory.register_singleton(bean_name, bean)

    def run(self, start_bean):
        # 加载配置
        log.info("********** 加载配置文件 **********")
        self.__create_environment()
        # 设置配置
        self._bean_factory.set_environment(self._environment)
        # 创建bean定义
        log.info("********** 扫描包，加载类信息 **********")
        bds = self.__create_bean_definitions()
        # 设置bd
        self._bean_factory.set_bean_definitions(bds)
        self._bean_factory.set_default_bean_postprocessor_classes(self._scanner.default_bean_postprocessor_classes)
        # 启动刷新
        log.info("********** 初始化流程 **********")
        self._bean_factory.refresh()
        # 找到启动类， 启动程序
        log.info("============== 执行main方法 ==============\n")
        self.__start(start_bean)

    def __start(self, start_bean):
        """
        找到奥启动类，调用启动方法 main
        :return:
        """

        # start_bean = self._bean_factory.get_bean(start_bean_name)
        # if start_bean is None:
        #     raise Exception("未找到启动类")

        start_bean.main(self)

    def set_config_directories(self, *config_directories):
        self.config_directories = config_directories

    def set_base_packages(self, *base_packages):
        self.base_packages = base_packages

    def __create_environment(self):
        sys_config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                                      "spring_resources")
        self._environment = self._environmentReader.read(*self.config_directories, sys_config_dir)

    def __create_bean_definitions(self):
        # 扫描自定义的组件
        all_custom_packages = self._scanner.get_all_custom_modules(self.__current_directory, *self.base_packages)
        # 排序
        all_custom_packages = sorted(list(set(all_custom_packages)))
        if self.__debug:
            log.info("找到所有包如下: \n" + "\n".join(all_custom_packages) + "\n")
        # print("all_custom_packages = ", all_custom_packages)

        self._scanner.set_evn(self._environment)

        return self._scanner.scan(*all_custom_packages)

    def get_bean(self, name):
        return self._bean_factory.get_bean(name)
