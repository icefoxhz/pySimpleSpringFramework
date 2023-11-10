from pySimpleSpringFramework.spring_aop.framework.autoproxy.advice import MethodBeforeAdvice, MethodAfterAdvice, \
    MethodThrowingAdvice, MethodAroundAdvice, MethodAfterReturningAdvice
from pySimpleSpringFramework.spring_core.proxy.proxy import DynamicProxy
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationName


class AbstractProxyCreator:
    def __init__(self):
        self._bean_factory = None
        self._proxy_objects = {}
        self._advice_types = {
            AnnotationName.BEFORE: MethodBeforeAdvice,
            AnnotationName.AFTER: MethodAfterAdvice,
            AnnotationName.AFTER_RETURNING: MethodAfterReturningAdvice,
            AnnotationName.AFTER_THROWING: MethodThrowingAdvice,
            AnnotationName.ROUND: MethodAroundAdvice,
        }

    def set_bean_factory(self, bean_factory):
        self._bean_factory = bean_factory

    def _add_proxy(self, bean_name, bean):
        self._proxy_objects[bean_name] = bean

    def _get_or_create_proxy_bean(self, target_name, target) -> DynamicProxy:
        """
        获取 / 创建代理对象
        :param target_name: 
        :param target: 
        :return: 
        """""
        # target 已经是代理对象了
        if isinstance(target, DynamicProxy):
            return target

        bean = self._proxy_objects.get(target_name, None)
        if bean is not None:
            return bean

        bean = DynamicProxy(target)
        self._add_proxy(target_name, bean)
        return bean
