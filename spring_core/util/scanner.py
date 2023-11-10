import inspect
import os
import pkgutil
import sys
from pySimpleSpringFramework.spring_beans.factory.annotation.simpleBeanDefinition import SimpleBeanDefinition
from pySimpleSpringFramework.spring_core.log import log
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationName, AnnotationType
from pySimpleSpringFramework.spring_core.util.base.concurrentDict import ConcurrentDict


class Scanner:
    def __init__(self, bean_factory):
        self._environment = None
        self._bean_factory = bean_factory
        self._bean_definitions = ConcurrentDict()
        self._default_bean_postprocessor_names = None
        self._default_bean_postprocessor_classes = {}

    @property
    def default_bean_postprocessor_classes(self):
        return self._default_bean_postprocessor_classes

    def set_evn(self, env):
        self._environment = env
        self._default_bean_postprocessor_names = self._environment.get("__pySpring_bean_postprocessor_names__", [])

    def scan(self, *package_names):
        self.__load_sys_classes()
        self.__scan_custom_packages(*package_names)
        return self._bean_definitions

    def __load_sys_classes(self):
        sys_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        package_names = self.get_all_sys_modules(sys_module_dir)
        if package_names is None:
            return

        for package_name in package_names:
            package = __import__(package_name, fromlist=[''])
            for loader, module_name, _ in pkgutil.walk_packages(package.__path__):
                module = loader.find_module(module_name).load_module(module_name)
                module_members = inspect.getmembers(module, inspect.isclass)
                for name, cls in module_members:
                    if name in self._default_bean_postprocessor_names:
                        self._default_bean_postprocessor_classes[name] = cls

    def __scan_custom_packages(self, *package_names):
        """
        扫描bean
        :return:
        """

        if package_names is None:
            return

        for package_name in package_names:
            package = __import__(package_name, fromlist=[''])
            self.__do_scan(package)

    def __do_scan(self, package):
        """
        模块走一遍，触发装饰器
        :param package:
        :return:
        """
        # print("package.__path__ = ", package.__path__)
        for loader, module_name, _ in pkgutil.walk_packages(package.__path__):
            module = loader.find_module(module_name).load_module(module_name)
            if module is None:
                continue

            # 遍历模块中的成员
            for name, obj in inspect.getmembers(module):
                # 检查是否是类, 且有 __bean_flag_dict__ 属性（判断是否要容器管理）
                annotation_attr = AnnotationType.get_annotation_attr(AnnotationName.COMPONENT)
                if inspect.isclass(obj) and hasattr(obj, annotation_attr):
                    cls = obj
                    # print(f"模块 {module_name} 中的类: {name}")
                    # print("cls.__name__ = ", cls.__name__)
                    self.__register_bean_definition(cls)

        # 注册系统用到的definitions
        self.__register_sys_bean_definitions()

    def __register_sys_bean_definitions(self):
        for class_name in self._default_bean_postprocessor_names:
            cls = self._default_bean_postprocessor_classes.get(class_name, None)
            if cls is None:
                raise Exception("类: {} 未找到".format(class_name))
            # 装饰成dComponent
            cls = Component(cls)
            # 设置 Order
            order_attr = AnnotationType.get_annotation_attr(AnnotationName.ORDER)
            setattr(cls, order_attr, -sys.maxsize)

            self.__register_bean_definition(cls)

    def __register_bean_definition(self, cls):
        if cls == object:
            return None

        model_path = self.__get_module_path_of_class(cls)
        # 改成首字母小写
        name = cls.__name__
        name = name[0].lower() + name[1:]

        if name in self._bean_definitions:
            # 判断是否已经加载过了，即同一个模块。 为了兼容模块下面 没有添加__init__.py 和 添加了 __init__.py 的2种情况
            had_bd = self._bean_definitions.get(name)
            # 同一个模块
            if had_bd.model_path == model_path:
                return
            # 不支持不同模块类名重复
            raise Exception("bean name: \"{}\" has already defined!".format(name))

        bd = SimpleBeanDefinition.generic_bean_definition(cls)
        bd.model_path = self.__get_module_path_of_class(cls)
        self._bean_definitions[name] = bd

    @staticmethod
    def __get_module_path_of_class(cls) -> str or None:
        # 使用inspect模块来获取类所在的模块路径
        module = inspect.getmodule(cls)
        if module is None:
            return None
        return module.__file__

    @staticmethod
    def get_all_sys_modules(base_package):
        module_path = base_package
        module_root_path = os.path.dirname(module_path)
        subdirectories = Scanner.__get_all_module_directories(module_path)
        subdirectories = [m.replace(module_root_path + os.sep, "").replace(os.sep, ".")
                          for m in subdirectories]
        return subdirectories

    @staticmethod
    def get_all_custom_modules(current_directory, *base_packages):
        """
        遍历获取所有modules
        :param current_directory:
        :param base_packages:
        :return:
        """
        # 获取当前目录
        current_file_dir = os.getcwd()
        return Scanner.__get_all_modules(current_file_dir, current_directory, *base_packages)

    @staticmethod
    def __get_all_modules(current_file_dir, current_directory, *base_packages):
        modules = []
        # module_root_path 应该是 pySimpleSpring 目录的父目录
        module_root_path = os.path.dirname(os.path.dirname(current_file_dir))
        log.info("======== module_root_path: " + module_root_path)

        for module in base_packages:
            # package是当前入口文件的相对位置， 例如 "../../a"
            module_path = os.path.abspath(os.path.join(current_directory, module))
            subdirectories = Scanner.__get_all_module_directories(module_path)
            subdirectories = [m.replace(module_root_path + os.sep, "").replace(os.sep, ".")
                              for m in subdirectories]
            modules += subdirectories
        return modules

    @staticmethod
    def __get_all_module_directories(root_directory):
        """
        获取目录下所有模块的目录和子目录
        :param root_directory:
        :return:
        """
        # 把当前目录也加进去
        subdirectories = [root_directory]
        for root, dirs, files in os.walk(root_directory):
            for d in dirs:
                if d.endswith("__pycache__"):
                    continue
                subdirectories.append(os.path.join(root, d))
        return subdirectories
