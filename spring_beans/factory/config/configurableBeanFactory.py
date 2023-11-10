import abc

from pySimpleSpringFramework.spring_beans.factory.beanFactory import BeanFactory
from pySimpleSpringFramework.spring_beans.factory.config.singletonBeanRegistry import SingletonBeanRegistry


class ConfigurableBeanFactory(SingletonBeanRegistry, BeanFactory, metaclass=abc.ABCMeta):
    # 默认的2个作用域
    SCOPE_SINGLETON = "singleton"
    SCOPE_PROTOTYPE = "prototype"

    @abc.abstractmethod
    def add_bean_postprocessor(self, bean_postprocessor):
        """
        添加后置处理器
        :param bean_postprocessor:
        :return:
        """
        pass

    @abc.abstractmethod
    def get_bean_postprocessor_count(self) -> int:
        """
        获取后置处理器数量
        :return:
        """
        pass

    @abc.abstractmethod
    def destroy_bean(self, bean_name):
        """
        手动释放对象
        :return:
        """
        pass

    @abc.abstractmethod
    def destroy_singletons(self):
        """
        手动释放所有单例对象
        :return:
        """
        pass
