# import copy
import importlib
import sys

from pySimpleSpringFramework.spring_aop.framework.annotation.classAnnotation import Aspect
from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import Pointcut
from pySimpleSpringFramework.spring_beans.factory.annotation.simpleBeanDefinition import SimpleBeanDefinition
from pySimpleSpringFramework.spring_beans.factory.config.configurableBeanFactory import ConfigurableBeanFactory
from pySimpleSpringFramework.spring_beans.factory.support.beanDefinitionRegistry import BeanDefinitionRegistry
from pySimpleSpringFramework.spring_beans.factory.support.defaultSingletonBeanRegistry import \
    DefaultSingletonBeanRegistry
from pySimpleSpringFramework.spring_context.applicationEnvironment import ApplicationEnvironment
from pySimpleSpringFramework.spring_core.log import log
from pySimpleSpringFramework.spring_core.proxy.proxy import DynamicProxy
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName
from pySimpleSpringFramework.spring_core.type.attrType import AttrJudgeName
from pySimpleSpringFramework.spring_core.util.base.concurrentDict import ConcurrentDict
from pySimpleSpringFramework.spring_core.util.commonUtils import is_instance, get_bean_name_by_class_name, \
    get_bean_name_by_class, get_nested_value
from pySimpleSpringFramework.spring_orm.dsAopTemplate import DataSourceAopTemplate


class DefaultBeanFactory(ConfigurableBeanFactory, BeanDefinitionRegistry, DefaultSingletonBeanRegistry):
    def __init__(self, debug=False):
        super().__init__()
        self.__debug = debug
        self._application_context = None
        self._prototype_new_cache = None
        self._bean_definitions = None
        self._environment = None
        self._default_bean_postprocessor_classes = None
        self._advisors = None

        self.__after_init()

    def __after_init(self):
        self._prototype_new_cache = ConcurrentDict()

    def set_application_context(self, application_context):
        self._application_context = application_context

    def refresh(self):
        # 清除所有单例bean
        self.clear_singleton_objects()

        # 把applicationContext注册进去
        self.register_singleton("applicationContext", self._application_context)

        # 创建配置bean
        if self.__debug:
            log.info(">>>>> 将读取的配置文件信息生成配置类")
        self.__create_application_environment()

        # 加载框架中使用到的beans
        if self.__debug:
            log.info(">>>>> 加载框架中使用到的beans")
        self.__load_default_beans()

        if self.__debug:
            log.info(">>>>>  加载系统创建的Aop beanDefinition")
        self.__add_sys_aop_bean_definitions()

        # bean_definitions_map 排序, 生成bean的顺序就是按bean_definitions_map的顺序来的
        if self.__debug:
            log.info(">>>>> 按Order装饰器对类定义进行排序")
        self.__do_order_bean_definitions()

        # 生成未执行注入的单例
        if self.__debug:
            log.info(">>>>> 生成未初始化的单例bean")
        self.__create_early_singletons()

        # 添加默认的 beanPostProcessors
        if self.__debug:
            log.info(">>>>> 添加默认的beanPostProcessors")
        self.__add_default_bean_postprocessors()

        # 未初始化的单例bean先执行aop
        if self.__debug:
            log.info(">>>>> 未初始化的单例bean执行aop")
        self.__do_aop()

        # 执行未初始化的单例的初始化流程
        if self.__debug:
            log.info(">>>>> 执行单例bean的初始化流程")
        self.__do_init_singletons()

        if self.__debug:
            log.info("====== beanFactory refresh completed ======")

    @staticmethod
    def __func_order(item) -> int:
        cls = item[1].cls
        order_attr = AnnotationType.get_annotation_attr(AnnotationName.ORDER)
        if hasattr(cls, order_attr):
            return getattr(cls, order_attr)
        return sys.maxsize

    def __do_order_bean_definitions(self):
        # 使用sorted函数和lambda表达式根据值排序
        self._bean_definitions = dict(sorted(self._bean_definitions.items(), key=self.__func_order))
        # print(self._bean_definitions_map)

    def __create_application_environment(self):
        instance = ApplicationEnvironment()
        instance.set_env(self._environment)
        self.register_singleton("applicationEnvironment", instance)

    def __load_default_beans(self):
        default_module_names = self._environment.get("__pySpring_default_module_names__", {})
        for module_full_name, class_name_str in default_module_names.items():
            class_names = class_name_str.split(",")
            for class_name in class_names:
                class_name = class_name.strip()
                # 动态导入模块
                module = importlib.import_module(module_full_name)
                class_obj = getattr(module, class_name)
                if class_obj is not None:
                    bean = class_obj()
                    if hasattr(bean, "set_environment"):
                        env = self.get_singleton("applicationEnvironment")
                        bean.set_environment(env)
                    if hasattr(bean, "set_bean_factory"):
                        bean.set_bean_factory(self)
                    if hasattr(bean, "after_init"):
                        bean.after_init()

                    name = get_bean_name_by_class_name(class_name)
                    self.register_singleton(name, bean)

    def __add_default_bean_postprocessors(self):
        postprocessors = []
        for bean in self._early_singletons.values():
            if is_instance(bean, AttrJudgeName.IS_BEAN_POSTPROCESSOR):
                postprocessor = bean
                postprocessor.set_bean_factory(self)
                self.add_bean_postprocessor(postprocessor)
                postprocessors.append(postprocessor)

        for postprocessor in postprocessors:
            bean_name = self.get_bean_name(postprocessor)
            self._early_singletons.pop(bean_name)

    def __create_early_singletons(self):
        """
        生成未执行注入的对象
        :return:
        """
        for name, bd in self._bean_definitions.items():
            if not self.is_singleton(name):
                continue

            # 已经生成了
            if self.get_singleton(name) is not None:
                continue

            # 创建不完整bean      __new__
            incomplete_bean = self.create_early_object_by_class(bd.cls)
            if incomplete_bean is None:
                continue

            self.register_early_singleton(name, incomplete_bean)

    def __do_init_singletons(self):
        for bean_name, bean in self._early_singletons.items():
            self.do_init_bean(bean_name, bean)
            self.register_singleton(bean_name, bean)
        # 清空
        self._early_singletons.clear()

    def do_init_bean(self, bean_name, bean):
        target = bean
        # 进行过aop了， 要获取原始对象进行操作
        if isinstance(bean, DynamicProxy):
            bean = bean.get_target()

        # 初始化前方法
        self.__post_processes_before_initialization(bean, bean_name)

        # 初始化方法 __init__
        bd = self._bean_definitions.get(bean_name)
        self.call_init__(bd, bean)

        # 找 @Value注入配置
        self.__do_value_inject(bean, bean_name)

        # 处理方法注入
        self.__do_inject(bean, bean_name)

        # 初始化后
        self.__post_process_after_initialization(bean, bean_name)

    def set_bean_definitions(self, bds):
        self._bean_definitions = bds

    def set_environment(self, environment):
        self._environment = environment

    def set_default_bean_postprocessor_classes(self, default_bean_postprocessor_classes):
        self._default_bean_postprocessor_classes = default_bean_postprocessor_classes

    @property
    def advisors(self):
        return self._advisors

    def get_proxy_creator(self):
        return self.get_bean("proxyCreator")

    def get_prototype_bean_creator(self):
        return self.get_bean("defaultPrototypeBeanCreator")

    @staticmethod
    def get_bean_name(bean):
        cls_name = bean.__class__.__name__
        return cls_name[0].lower() + cls_name[1:]

    def get_bean(self, name) -> object or None:
        # 先直接去单例池拿，因为有些系统bean不生成beanDefinition,而是直接生成到单例池中的
        bean = self.get_singleton(name)
        if bean is not None:
            return bean

        scope = self.get_bean_scope(name)
        if scope == "prototype":
            prototypeBeanCreator = self.get_prototype_bean_creator()
            return prototypeBeanCreator.get_prototype(name)

        return None

    def contains_bean(self, name) -> bool:
        """
        包含原型bean
        :param name:
        :return:
        """
        is_singleton = self.is_singleton(name)
        if is_singleton:
            return name in self._singleton_objects
        return name in self._bean_definitions

    def is_singleton(self, name) -> bool:
        scope = self.get_bean_scope(name)
        return scope == "singleton"

    def get_bean_scope(self, name):
        if name not in self._bean_definitions:
            raise Exception("bean name: {} 不存在定义".format(name))
        bean_definition = self._bean_definitions.get(name)
        annotation_metadata = bean_definition.get_annotation_metadata()
        scope = annotation_metadata.get_class_annotation(AnnotationName.SCOPE)
        return scope

    def register_bean_definition(self, bean_name, bean_definition):
        self._bean_definitions[bean_name] = bean_definition

    def remove_Bean_definition(self, bean_name):
        if bean_name in self._bean_definitions:
            self._bean_definitions.remove(bean_name)

    def get_bean_definition(self, bean_name) -> SimpleBeanDefinition:
        return self._bean_definitions.get(bean_name)

    def contains_bean_definition(self, bean_name):
        return bean_name in self._bean_definitions

    def get_bean_definition_names(self) -> list:
        return list(self._bean_definitions.keys())

    def get_bean_definition_count(self) -> int:
        return self._bean_definitions.size

    def add_bean_postprocessor(self, bean_postprocessor):
        self.register_singleton(self.get_bean_name(bean_postprocessor), bean_postprocessor)

    def get_bean_postprocessor_count(self) -> int:
        count = 0
        for bean in self._singleton_objects.values():
            if is_instance(bean, AttrJudgeName.IS_INITIALIZATION_BEAN_POSTPROCESSOR):
                count += 1
        return count

    def destroy_bean(self, bean_name):
        if bean_name in self._singleton_objects:
            self._singleton_objects.remove(bean_name)

    def destroy_singletons(self):
        self._singleton_objects.clear_singleton_objects()

    def create_early_object_by_class(self, cls) -> object:
        """
        创建 bean对象， 不会调用  __init__ 方法
        :param cls:
        :return:
        """
        # 会导致序列化报错，不能用copy
        # if self._prototype_new_cache.contains_key(cls):
        #     return copy.deepcopy(self._prototype_new_cache.get(cls))

        instance = object.__new__(cls)
        self._prototype_new_cache[cls] = instance
        return instance

    def __invoke_bean_post_processor(self, target_name, target, before_or_after, attr_judge_name):
        for bean in self._singleton_objects.values():
            if is_instance(bean, attr_judge_name):
                bean_post_processor = bean
                bean_post_processor.set_bean_factory(self)

                if before_or_after == "before":
                    target = bean_post_processor.post_process_before_initialization(target_name, target)
                if before_or_after == "after":
                    target = bean_post_processor.post_process_after_initialization(target_name, target)

                if target is None:
                    break

    def __post_processes_before_initialization(self, target, target_name):
        """
        执行所有的初始化后置处理器的 post_process_before_initialization 方法
        :param target:
        :param target_name:
        :return:
        """
        self.__invoke_bean_post_processor(target_name,
                                          target,
                                          "before",
                                          AttrJudgeName.IS_INITIALIZATION_BEAN_POSTPROCESSOR)

    def __post_process_after_initialization(self, target, target_name):
        """
        执行所有的初始化后置处理器的 post_process_after_initialization 方法
        :param target:
        :param target_name:
        :return:
        """
        self.__invoke_bean_post_processor(target_name,
                                          target,
                                          "after",
                                          AttrJudgeName.IS_INITIALIZATION_BEAN_POSTPROCESSOR)

    @staticmethod
    def call_init__(bd, target):
        bean_metadata = bd.get_bean_metadata()
        method, method_arg_names = bean_metadata.get_init_method()

        # 如果__init__无参数
        if method_arg_names is None or len(method_arg_names) == 0:
            target.__init__()
            return

        # 如果__init__有参数，则先全部给 None
        param_count = len(method_arg_names)
        params = [None] * param_count
        target.__init__(*params)

    def __do_inject(self, target, target_name):
        """
        只支持set注入，即以set开头的方法
        :param target:
        :param target_name:
        :return:

        """

        self.__invoke_bean_post_processor(target_name,
                                          target,
                                          "after",
                                          AttrJudgeName.IS_AUTOWIRED_BEAN_POSTPROCESSOR)

    def __do_value_inject(self, bean, bean_name):
        """
        @Value 是用在方法上的
        :param bean:
        :param bean_name:
        :return:
        """
        bd = self.get_bean_definition(bean_name)
        if bd is None:
            return

        annotation_metadata = bd.get_annotation_metadata()
        bean_metadata = bd.get_bean_metadata()

        methods = annotation_metadata.get_methods(AnnotationName.VALUE)
        for method, annotation_value in methods.items():
            arg_names = bean_metadata.get_method_arg_names(method)
            attrs = bean_metadata.attrs

            for config_key, attr_name in annotation_value.items():
                if attr_name not in attrs.keys():
                    log.warning("警告: 类[ {} ]中没有属性[ {} ]，跳过设置，请先在 __init__中添加！".
                                format(bean_metadata.cls.__name__, attr_name))
                    continue

                if config_key is None:
                    log.warning("警告: 配置文件中没有找到key: {}， 跳过设置".format(config_key))
                    continue

                config_val = get_nested_value(config_key, self._environment)
                rel_attr_name = attrs[attr_name]
                setattr(bean, rel_attr_name, config_val)

    def __get_advisors(self):
        result = {}
        aspect_attr = AnnotationType.get_annotation_attr(AnnotationName.ASPECT)
        for bean_name, bean in self._early_singletons.items():
            if hasattr(bean, aspect_attr):
                result[bean_name] = bean

        # 从 early中移除， 放到 singletons中
        for bean_name, bean in result.items():
            self._early_singletons.pop(bean_name)
            self.register_singleton(bean_name, bean)

        return result

    def __do_create_proxy(self, proxy_creator):
        self._advisors = self.__get_advisors()
        for bean_name, bean in self._early_singletons.items():
            proxy_bean = proxy_creator.create(bean_name, bean)

            # 没有生成代理
            if proxy_bean == bean:
                continue

            # 替换老的bean
            self._early_singletons[bean_name] = proxy_bean

    def __do_aop(self):
        proxy_creator = self.get_proxy_creator()
        self.__do_create_proxy(proxy_creator)

    @staticmethod
    def __add_execution(method_map, pointcut, bd):
        executions = pointcut.get("execution")
        for method in method_map.keys():
            execution_str = bd.cls.__name__ + "." + method.__name__
            executions.append(execution_str)
        return {"execution": executions}

    def __add_sys_aop_bean_definitions(self):
        self.__add_ds_aop_bean_definition()

    def __add_ds_aop_bean_definition(self):
        if not self.contains_singleton("databaseManager"):
            return

        ds_pointcut = {"execution": []}
        select_pointcut = {"execution": []}
        trans_pointcut = {"execution": []}
        execute_pointcut = {"execution": []}

        for bd in self._bean_definitions.values():
            meta_obj = bd.get_ds_metadata()
            if meta_obj is None:
                continue

            metadata_map = meta_obj.ds_metadata
            for anno_name, method_map in metadata_map.items():
                if anno_name == AnnotationName.DS:
                    ds_pointcut = self.__add_execution(method_map, ds_pointcut, bd)
                elif anno_name == AnnotationName.SELECT:
                    select_pointcut = self.__add_execution(method_map, select_pointcut, bd)
                elif anno_name == AnnotationName.TRANSACTIONAL:
                    trans_pointcut = self.__add_execution(method_map, trans_pointcut, bd)
                elif anno_name == AnnotationName.EXECUTE:
                    execute_pointcut = self.__add_execution(method_map, execute_pointcut, bd)

        flag = False
        # 调用装饰器，添加进去
        if len(ds_pointcut["execution"]) > 0:
            decorator_pointcut = Pointcut(ds_pointcut)
            DataSourceAopTemplate.aspectPointcutDs = decorator_pointcut(DataSourceAopTemplate.aspectPointcutDs)
            flag = True

        if len(select_pointcut["execution"]) > 0:
            decorator_select = Pointcut(select_pointcut)
            DataSourceAopTemplate.aspectPointcutSelect = decorator_select(DataSourceAopTemplate.aspectPointcutSelect)
            flag = True

        if len(trans_pointcut["execution"]) > 0:
            decorator_trans = Pointcut(trans_pointcut)
            DataSourceAopTemplate.aspectPointcutTransactional = decorator_trans(
                DataSourceAopTemplate.aspectPointcutTransactional)
            flag = True

        if len(execute_pointcut["execution"]) > 0:
            decorator_exec = Pointcut(execute_pointcut)
            DataSourceAopTemplate.aspectPointcutExecute = decorator_exec(DataSourceAopTemplate.aspectPointcutExecute)
            flag = True

        if flag:
            template_class = Aspect(DataSourceAopTemplate)
            name = get_bean_name_by_class(template_class)

            bd = SimpleBeanDefinition(DataSourceAopTemplate)
            self.register_bean_definition(name, bd)

            bean = template_class()
            databaseManager = self.get_bean("databaseManager")
            bean.set_db_manager(databaseManager)
            bean.set_environment(self.get_singleton("applicationEnvironment"))
            self._early_singletons[name] = bean
