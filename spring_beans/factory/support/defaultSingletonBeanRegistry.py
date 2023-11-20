import threading
from pySimpleSpringFramework.spring_beans.factory.config.singletonBeanRegistry import SingletonBeanRegistry
from pySimpleSpringFramework.spring_core.util.base.concurrentDict import ConcurrentDict


class DefaultSingletonBeanRegistry(SingletonBeanRegistry):

    def __init__(self):
        self._lock = threading.Lock()
        self._singleton_objects = ConcurrentDict()
        self._early_singletons = {}

    def __reduce__(self):
        # 在序列化过程中排除线程锁
        return self.__class__, ()

    def clear_singleton_objects(self):
        with self._lock:
            self._singleton_objects.clear()
        self._early_singletons.clear()

    def _add_singleton(self, bean_name, singleton_object):
        with self._lock:
            self._singleton_objects[bean_name] = singleton_object

    def register_early_singleton(self, bean_name, singleton_object):
        self._early_singletons[bean_name] = singleton_object

    def register_singleton(self, bean_name, singleton_object):
        with self._lock:
            if self.contains_singleton(bean_name):
                raise Exception("无法注册当前对象, bean name: {} 已经存在".format(bean_name))
        self._add_singleton(bean_name, singleton_object)

    def _get_singleton(self, bean_name, allow_early) -> object or None:
        bean = self._singleton_objects.get(bean_name)
        if bean is not None:
            return bean
        if allow_early:
            early_bean = self._early_singletons.get(bean_name, None)
            return early_bean

    def get_singleton(self, bean_name) -> object:
        return self._get_singleton(bean_name, True)

    def contains_singleton(self, bean_name) -> bool:
        return self._singleton_objects.contains_key(bean_name)

    def get_singleton_names(self) -> list:
        return list(self._singleton_objects.keys())

    def get_singleton_count(self) -> int:
        return self._singleton_objects.size

# class DefaultSingletonBeanRegistry(SingletonBeanRegistry):
#
#     def __init__(self):
#         self._singleton_objects = {}
#         self._early_singletons = {}
#
#     def clear_singleton_objects(self):
#         self._singleton_objects.clear()
#         self._early_singletons.clear()
#
#     def _add_singleton(self, bean_name, singleton_object):
#         self._singleton_objects[bean_name] = singleton_object
#
#     def register_early_singleton(self, bean_name, singleton_object):
#         self._early_singletons[bean_name] = singleton_object
#
#     def register_singleton(self, bean_name, singleton_object):
#         if self.contains_singleton(bean_name):
#             raise Exception("无法注册当前对象, bean name: {} 已经存在".format(bean_name))
#         self._add_singleton(bean_name, singleton_object)
#
#     def _get_singleton(self, bean_name, allow_early) -> object or None:
#         bean = self._singleton_objects.get(bean_name)
#         if bean is not None:
#             return bean
#         if allow_early:
#             early_bean = self._early_singletons.get(bean_name, None)
#             return early_bean
#
#     def get_singleton(self, bean_name) -> object:
#         return self._get_singleton(bean_name, True)
#
#     def contains_singleton(self, bean_name) -> bool:
#         return bean_name in self._singleton_objects.keys()
#
#     def get_singleton_names(self) -> list:
#         return list(self._singleton_objects.keys())
#
#     def get_singleton_count(self) -> int:
#         return len(self._singleton_objects)
