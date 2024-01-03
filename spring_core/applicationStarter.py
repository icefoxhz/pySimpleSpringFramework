import abc

from pySimpleSpringFramework.spring_context.annotation.simpleApplicationContext import SimpleApplicationContext
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName


class ApplicationStarter:
    """
    入口启动类，给子类继承
    """

    def __init__(self):
        self.__app = None
        self._paramDict = None

    def run(self, paramDict=None, debug=False):
        """
        :param paramDict:
        :param debug:
        """
        component_scan_attr = AnnotationType.get_annotation_attr(AnnotationName.COMPONENT_SCAN)
        if not hasattr(self, component_scan_attr):
            raise Exception("未找到扫描路径！请用@ComponentScan")

        config_path_attr = AnnotationType.get_annotation_attr(AnnotationName.CONFIG_PATH)
        if not hasattr(self, config_path_attr):
            raise Exception("未找到配置文件目录！请用@ConfigDirectories")

        self._paramDict = paramDict

        base_config_path = getattr(self, config_path_attr)
        base_packages = getattr(self, component_scan_attr)
        # base_packages = list(base_packages)
        # base_packages.append("../" + os.getcwd().split(os.sep)[-1])

        self.__app = SimpleApplicationContext(debug)
        self.__app.set_config_directories(*base_config_path)
        self.__app.set_base_packages(*base_packages)
        # start_bean_name = self.__class__.__name__
        # start_bean_name = start_bean_name[0].lower() + start_bean_name[1:]
        self.__app.run()

        self.main()

    @property
    def application_context(self):
        return self.__app

    @abc.abstractmethod
    def main(self):
        pass
