import abc

from pySimpleSpringFramework.spring_context.support.beanPostProcessor import BeanPostProcessor
from pySimpleSpringFramework.spring_core.type.attrType import AttrJudgeType, AttrJudgeName


class AbstractInitializationBeanPostProcessor(BeanPostProcessor, metaclass=abc.ABCMeta):
    _before_method_names = ["before_init", "_before_init"]
    _after_method_names = ["after_init", "_after_init"]

    def _invoke(self, bean_name, bean, method_name) -> bool:
        bean_definition = self._bean_factory.get_bean_definition(bean_name)
        bean_metadata = bean_definition.get_bean_metadata()
        args = bean_metadata.get_method_arg_names(method_name)
        if args is not None:
            raise Exception("类: {} 的方法: {} 不能有参数！".format(bean_metadata.class_name, method_name))
        method = bean_metadata.get_method(method_name)
        if method is not None:
            method(bean)
            return True
        return False


setattr(AbstractInitializationBeanPostProcessor,
        AttrJudgeType.get_attr_name(AttrJudgeName.IS_INITIALIZATION_BEAN_POSTPROCESSOR), True)
