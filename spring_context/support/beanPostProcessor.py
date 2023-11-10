import abc

from pySimpleSpringFramework.spring_core.type.attrType import AttrJudgeName, AttrJudgeType


class BeanPostProcessor(metaclass=abc.ABCMeta):
    _bean_factory = None

    def set_bean_factory(self, bean_factory):
        self._bean_factory = bean_factory

    @abc.abstractmethod
    def post_process_before_initialization(self, bean_name, bean) -> object or None:
        pass

    @abc.abstractmethod
    def post_process_after_initialization(self, bean_name, bean) -> object or None:
        pass


setattr(BeanPostProcessor, AttrJudgeType.get_attr_name(AttrJudgeName.IS_BEAN_POSTPROCESSOR), True)
