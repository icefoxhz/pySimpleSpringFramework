import inspect

from pySimpleSpringFramework.spring_core.util.commonUtils import is_custom_function


class BeanMetadata:
    def __init__(self, cls):
        self.cls = cls
        # 显示名 => 真实名。 因为 self.__xx 这种的实际属性名是这样的： _NewClass__xx ，而不是 __xx
        self._attrs = {}
        # 方法 和 所有参数名
        self._method_arg_names = {}
        self._methods = {}
        self._init_arg_names = None

        self.__after_init()

    def __after_init(self):
        self.__add_init_method()

    def get_methods(self) -> list:
        return list(self._method_arg_names.keys())

    def get_method(self, method_name) -> object or None:
        return self._methods.get(method_name, None)

    def get_method_arg_names(self, method):
        return self._method_arg_names.get(method, None)

    def get_init_method(self):
        method = self._methods.get("__init__", None)
        method_arg_names = self._method_arg_names.get(method, None)
        return method, method_arg_names

    def __add_init_method(self):
        init_method = self.cls.__init__
        # 默认 __init__ 函数
        if init_method is object.__init__:
            self._init_arg_names = None
            return

        # 自定义的 __init__ 函数，获取参数
        parameters = inspect.signature(init_method).parameters
        # 去掉参数中的 'self'
        self._init_arg_names = [param for param in parameters if param != 'self']
        self._init_arg_names = None if len(self._init_arg_names) == 0 else self._init_arg_names

    def add_method(self, method_name, method, arg_names):
        self._methods[method_name] = method
        self._method_arg_names[method] = arg_names

    def add_attr(self, attr_name, real_attr_name):
        self._attrs[attr_name] = real_attr_name

    def add_attrs(self, attrs):
        self._attrs.update(attrs)

    @property
    def attrs(self):
        return self._attrs

    def contains_attr(self, attr_name) -> bool:
        return attr_name in self._attrs.keys()

    def contains_method(self, method_name) -> bool:
        return method_name in self._methods.keys()

    def get_custom_attributes(self):
        """
       获取实例中定义的属性
       :return:  显示属性名: 实际属性名 .  因为 self.__xx 这种的实际属性名是这样的： _NewClass__xx ，而不是 __xx
       """
        # 创建个临时的实例，用于获取属性
        instance = self.cls(self._init_arg_names) if self._init_arg_names is not None else self.cls()

        private_prefix = "_" + instance.__class__.__name__
        for real_attr in dir(instance):
            if not callable(getattr(instance, real_attr)) and not real_attr.startswith("__") and not real_attr.endswith("__"):
                display_attr = real_attr if not real_attr.startswith(private_prefix) else real_attr.replace(private_prefix, "")
                self.add_attr(display_attr, real_attr)

        del instance

    def get_custom_methods(self):
        # 获取所有非系统方法. 这里获取的 methods 是和父类合并过的
        methods = inspect.getmembers(self.cls, is_custom_function)
        for method_name, method in methods:
            # 获取方法的参数
            if inspect.isfunction(method) or inspect.ismethod(method):
                parameters = inspect.signature(method).parameters
                # 去掉参数中的 'self'
                parameter_names = [param for param in parameters if param != 'self']
                self.add_method(method_name, method, parameter_names)

    @staticmethod
    def introspect(cls):
        beanMetadata = BeanMetadata(cls)
        # 获取所有非系统方法. 这里获取的 methods 是和父类合并过的
        beanMetadata.get_custom_methods()
        # 获取所有非系统属性，这里获取的 methods 是和父类合并过的
        beanMetadata.get_custom_attributes()
        return beanMetadata
