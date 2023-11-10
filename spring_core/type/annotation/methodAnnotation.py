from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName


def Value(val):
    """
    自动注入配置
    :param val:
    :return:
    """

    def decorator(method):
        value_attr = AnnotationType.get_annotation_attr(AnnotationName.VALUE)
        if not hasattr(method, value_attr):
            setattr(method, value_attr, val)
        return method

    return decorator


def Autowired(func):
    """
    自动注入， 仅作用在方法上，且方法名称必须符合规范（名称以 set 或 _set 或 __set 开头）
    :param func:
    :return:
    """
    autowired_attr = AnnotationType.get_annotation_attr(AnnotationName.AUTOWIRED)
    if not hasattr(func, autowired_attr):
        setattr(func, autowired_attr, True)
    return func
