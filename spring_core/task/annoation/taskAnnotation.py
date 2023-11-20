from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName


def Sync(target):
    if isinstance(target, type):
        raise Exception("Sync 仅装饰方法")
    attr = AnnotationType.get_annotation_attr(AnnotationName.SYNC)
    setattr(target, attr, True)
    return target


def NewThreadPool(target):
    if isinstance(target, type):
        raise Exception("Sync 仅装饰方法")
    attr = AnnotationType.get_annotation_attr(AnnotationName.NEW_THREAD_POOL)
    setattr(target, attr, True)
    return target
