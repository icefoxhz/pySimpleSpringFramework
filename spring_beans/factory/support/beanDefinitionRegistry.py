import abc

from pySimpleSpringFramework.spring_beans.factory.annotation.simpleBeanDefinition import SimpleBeanDefinition


class BeanDefinitionRegistry(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def register_bean_definition(self, bean_name, bean_definition):
        pass

    @abc.abstractmethod
    def remove_Bean_definition(self, bean_name):
        pass

    @abc.abstractmethod
    def get_bean_definition(self, bean_name) -> SimpleBeanDefinition:
        pass

    @abc.abstractmethod
    def contains_bean_definition(self, bean_name):
        pass

    @abc.abstractmethod
    def get_bean_definition_names(self) -> list:
        pass

    @abc.abstractmethod
    def get_bean_definition_count(self) -> int:
        pass
