import inspect

from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName, Propagation
from pySimpleSpringFramework.spring_core.util.commonUtils import is_custom_function


def DS(datasource_name):
    """
    设置当前数据源名称
    :param datasource_name:
    :return:
    """

    def decorator(target):
        ds_attr = AnnotationType.get_annotation_attr(AnnotationName.DS)
        autowired_attr = AnnotationType.get_annotation_attr(AnnotationName.AUTOWIRED)
        # 参数是一个类
        if isinstance(target, type):
            # 给所有自定义函数加上标记
            functions = inspect.getmembers(target, is_custom_function)
            for _, function_obj in functions:
                if function_obj.__name__ == "__init__":
                    continue

                if hasattr(function_obj, autowired_attr):
                    continue

                # 如果已经被标记了就说明是函数上有 @DS，就跳过
                if hasattr(function_obj, ds_attr):
                    continue
                setattr(function_obj, ds_attr, datasource_name)
        # 参数是一个函数
        elif callable(target):
            setattr(target, ds_attr, datasource_name)
        return target

    return decorator


def Select(sql):
    def decorator(target):
        if isinstance(target, type):
            raise Exception("Select 仅装饰方法")
        attr = AnnotationType.get_annotation_attr(AnnotationName.SELECT)
        setattr(target, attr, sql)
        return target

    return decorator


def Insert(sql):
    def decorator(target):
        if isinstance(target, type):
            raise Exception("Insert 仅装饰方法")
        attr = AnnotationType.get_annotation_attr(AnnotationName.EXECUTE)
        setattr(target, attr, sql)
        return target

    return decorator


def Update(sql):
    def decorator(target):
        if isinstance(target, type):
            raise Exception("Update 仅装饰方法")
        attr = AnnotationType.get_annotation_attr(AnnotationName.EXECUTE)
        setattr(target, attr, sql)
        return target

    return decorator


def Delete(sql):
    def decorator(target):
        if isinstance(target, type):
            raise Exception("Delete 仅装饰方法")
        attr = AnnotationType.get_annotation_attr(AnnotationName.EXECUTE)
        setattr(target, attr, sql)
        return target

    return decorator


def Transactional(propagation=Propagation.REQUIRED):
    def decorator(target):
        attr = AnnotationType.get_annotation_attr(AnnotationName.TRANSACTIONAL)
        autowired_attr = AnnotationType.get_annotation_attr(AnnotationName.AUTOWIRED)
        # 参数是一个类
        if isinstance(target, type):
            # 给所有自定义函数加上标记
            functions = inspect.getmembers(target, is_custom_function)
            for _, function_obj in functions:
                if function_obj.__name__ == "__init__":
                    continue

                if hasattr(function_obj, autowired_attr):
                    continue

                # 如果已经被标记了就说明是函数上有 @Transactional，就跳过
                if hasattr(function_obj, attr):
                    continue
                setattr(function_obj, attr, propagation.value)
        # 参数是一个函数
        elif callable(target):
            setattr(target, attr, propagation.value)
        return target

    return decorator

