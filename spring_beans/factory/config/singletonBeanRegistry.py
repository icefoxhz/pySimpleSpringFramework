import abc


class SingletonBeanRegistry(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def register_singleton(self, bean_name, singleton_object):
        """
        手动将一个单例对象注册到容器中
        :param bean_name:
        :param singleton_object:
        :return:
        """
        pass

    @abc.abstractmethod
    def get_singleton(self, bean_name) -> object or None:
        """
        从容器中获取一个单例对象
        :param bean_name:
        :return:
        """
        pass

    @abc.abstractmethod
    def contains_singleton(self, bean_name) -> bool:
        """
        容器中是否包含一个单例对象
        :param bean_name:
        :return:
        """
        pass

    @abc.abstractmethod
    def get_singleton_names(self) -> list:
        """
        获取容器中所有单例对象的名称
        :return:
        """
        pass

    @abc.abstractmethod
    def get_singleton_count(self) -> int:
        """
        获取容器中所有单例对象的数量
        :return:
        """
        pass
