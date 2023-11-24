import time
from enum import Enum


class AnnotationName(Enum):
    COMPONENT_SCAN = 0
    CONFIG_PATH = 1
    COMPONENT = 2
    ORDER = 3
    AUTOWIRED = 4
    VALUE = 5
    SCOPE = 6

    ASPECT = 7
    POINTCUT = 8
    BEFORE = 9
    AFTER = 10
    AFTER_RETURNING = 11
    AFTER_THROWING = 12
    ROUND = 13

    DS = 14
    SELECT = 15
    EXECUTE = 16
    TRANSACTIONAL = 17


class AnnotationType:
    __timestamp = str(int(time.time()))

    types = {
        AnnotationName.COMPONENT: "__component__" + __timestamp,
        AnnotationName.COMPONENT_SCAN: "__component_scan__" + __timestamp,
        AnnotationName.CONFIG_PATH: "__config_path__" + __timestamp,
        AnnotationName.ORDER: "__order__" + __timestamp,
        AnnotationName.AUTOWIRED: "__autowired__" + __timestamp,
        AnnotationName.VALUE: "__value__" + __timestamp,
        AnnotationName.SCOPE: "__scope__" + __timestamp,

        AnnotationName.ASPECT: "__aspect__" + __timestamp,
        AnnotationName.POINTCUT: "__pointcut__" + __timestamp,
        AnnotationName.BEFORE: "__before__" + __timestamp,
        AnnotationName.AFTER: "__after__" + __timestamp,
        AnnotationName.AFTER_RETURNING: "__after_returning__" + __timestamp,
        AnnotationName.AFTER_THROWING: "__after_throwing__" + __timestamp,
        AnnotationName.ROUND: "__round__" + __timestamp,

        AnnotationName.DS: "__ds__" + __timestamp,
        AnnotationName.SELECT: "__db_select__" + __timestamp,
        AnnotationName.EXECUTE: "__db_execute__" + __timestamp,
        AnnotationName.TRANSACTIONAL: "__transactional__" + __timestamp,
    }

    @staticmethod
    def get_annotation_attr(annotation_name):
        return AnnotationType.types.get(annotation_name, None)


class Propagation(Enum):
    REQUIRED = 0
    REQUIRES_NEW = 1
