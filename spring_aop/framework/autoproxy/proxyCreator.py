import inspect

from pySimpleSpringFramework.spring_aop.framework.autoproxy.adviceTarget import AdviceTarget
from pySimpleSpringFramework.spring_aop.framework.autoproxy.abstractProxyCreator import AbstractProxyCreator
from pySimpleSpringFramework.spring_beans.factory.support.defaultBeanFactory import DefaultBeanFactory
from pySimpleSpringFramework.spring_core.util.commonUtils import get_bean_name_by_class_name, get_class_name_from_method


class ProxyCreator(AbstractProxyCreator):
    def __init__(self):
        super().__init__()
        self._bean_factory = None

    def set_bean_factory(self, bean_factory: DefaultBeanFactory):
        self._bean_factory = bean_factory

    def __filter_methods(self, bean, method_name) -> list:
        if method_name == "*":
            return self.__get_all_methods(bean)

        if hasattr(bean, method_name):
            return [getattr(bean, method_name)]

        return []

    @staticmethod
    def __get_all_methods(bean) -> list:
        """
        获取某个对象的所有方法
        :param bean:
        :return:
        """
        return [getattr(bean, method[0]) for method in inspect.getmembers(bean, predicate=inspect.ismethod)]

    def __create_advice(self, key) -> object or None:
        """
        创建对应类型的advice
        :param key:
        :return:
        """
        advice_class = self._advice_types.get(key, None)
        return advice_class() if advice_class is not None else None

    def create(self, target_name, target):
        """
        原对象进行aop,添加切入逻辑, 生成代理对象。  如果不需要aop，则返回原对象
        """
        for advisor_name in self._bean_factory.advisors.keys():
            # 不需要aop， 返回原对象
            bd = self._bean_factory.get_bean_definition(advisor_name)
            if bd is None:
                continue

            # 不需要aop， 返回原对象
            aop_metadata = bd.get_aop_metadata()
            if aop_metadata is None:
                continue

            # 不需要aop， 返回原对象
            if target_name not in aop_metadata.candidate_bean_names and "*" not in aop_metadata.candidate_bean_names:
                continue

            self.__do_create(target_name, target, aop_metadata)

        proxy_bean = self._proxy_objects.get(target_name, target)
        self._proxy_objects.clear()
        return proxy_bean

    def __do_create(self, target_name, target, aop_metadata):
        for advice_pos, advice_meta in aop_metadata.advices.items():
            for advice_method, point_cut_names in advice_meta.items():
                # 要用类实例的方法
                advice_method = self.get_object_method(advice_method)

                for point_cut_name in point_cut_names:
                    pointcuts_parsed_meta = aop_metadata.pointcuts_parsed.get(point_cut_name)
                    if pointcuts_parsed_meta is None:
                        continue

                    for class_name, method_names in pointcuts_parsed_meta.items():
                        bean_name = get_bean_name_by_class_name(class_name)

                        # 不是当前要处理的bean
                        if bean_name != target_name and bean_name != "*":
                            continue

                        # 所以需要切入的方法
                        target_methods = []
                        for method_name in method_names:
                            target_methods += self.__filter_methods(target, method_name)
                        # 去重
                        target_methods = list(set(target_methods))
                        if len(target_methods) == 0:
                            continue

                        #                              切入逻辑        目标bean    目标方法
                        advice_target = AdviceTarget(advice_method, target, target_methods)

                        #  切入逻辑类（通知类）
                        advice = self.__create_advice(advice_pos)
                        if advice is not None:
                            advice.set_advice_target(advice_target)
                            # 获取/ 创建代理对象
                            proxy_bean = self._get_or_create_proxy_bean(target_name, target)
                            if proxy_bean is not None:
                                proxy_bean.add_advice(advice)

    def get_object_method(self, advice_method):
        advice_class_name = get_class_name_from_method(advice_method)
        advice_bean_name = get_bean_name_by_class_name(advice_class_name)
        advice_method_name = advice_method.__name__
        advice_bean = self._bean_factory.get_bean(advice_bean_name)
        advice_method = getattr(advice_bean, advice_method_name)
        return advice_method
