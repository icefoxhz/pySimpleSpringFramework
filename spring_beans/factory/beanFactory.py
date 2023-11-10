import abc


class BeanFactory(abc.ABC):

    @abc.abstractmethod
    def get_bean(self, name) -> object or None:
        pass

    @abc.abstractmethod
    def contains_bean(self, name) -> bool:
        pass

    @abc.abstractmethod
    def is_singleton(self, name) -> bool:
        pass
