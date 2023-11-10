import sys

from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName


def Pointcut(execution_dict):
    def decorator(method):
        if isinstance(method, type):
            raise Exception("Pointcut 仅装饰方法")
        pointcut_attr = AnnotationType.get_annotation_attr(AnnotationName.POINTCUT)
        setattr(method, pointcut_attr, execution_dict)
        return method

    return decorator


def Before(pointcuts):
    def decorator(method):
        if isinstance(method, type):
            raise Exception("Before 仅装饰方法")
        before_attr = AnnotationType.get_annotation_attr(AnnotationName.BEFORE)
        setattr(method, before_attr, pointcuts)
        return method

    return decorator


def After(pointcuts):
    def decorator(method):
        if isinstance(method, type):
            raise Exception("After 仅装饰方法")
        after_attr = AnnotationType.get_annotation_attr(AnnotationName.AFTER)
        setattr(method, after_attr, pointcuts)
        return method

    return decorator


def AfterReturning(pointcuts):
    def decorator(method):
        if isinstance(method, type):
            raise Exception("AfterReturning 仅装饰方法")
        after_returning_attr = AnnotationType.get_annotation_attr(AnnotationName.AFTER_RETURNING)
        setattr(method, after_returning_attr, pointcuts)
        return method

    return decorator


def AfterThrowing(pointcuts):
    def decorator(method):
        if isinstance(method, type):
            raise Exception("AfterThrowing 仅装饰方法")
        after_throwing_attr = AnnotationType.get_annotation_attr(AnnotationName.AFTER_THROWING)
        setattr(method, after_throwing_attr, pointcuts)
        return method

    return decorator


def Around(pointcuts):
    def decorator(method):
        if isinstance(method, type):
            raise Exception("Around 仅装饰方法")
        round_attr = AnnotationType.get_annotation_attr(AnnotationName.ROUND)
        setattr(method, round_attr, pointcuts)
        return method

    return decorator
