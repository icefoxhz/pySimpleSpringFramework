import time
from enum import Enum


class AttrJudgeName(Enum):
    IS_BEAN_POSTPROCESSOR = 0
    IS_INITIALIZATION_BEAN_POSTPROCESSOR = 1
    IS_AUTOWIRED_BEAN_POSTPROCESSOR = 2


class AttrJudgeType:
    __timestamp = str(int(time.time()))

    types = {
        AttrJudgeName.IS_BEAN_POSTPROCESSOR: "__is_bean_postprocessor__" + __timestamp,
        AttrJudgeName.IS_INITIALIZATION_BEAN_POSTPROCESSOR: "__is_init_bean_postprocessor__" + __timestamp,
        AttrJudgeName.IS_AUTOWIRED_BEAN_POSTPROCESSOR: "__is_autowired_bean_postprocessor__" + __timestamp,
    }

    @staticmethod
    def get_attr_name(attr_judge_name):
        return AttrJudgeType.types.get(attr_judge_name, None)
