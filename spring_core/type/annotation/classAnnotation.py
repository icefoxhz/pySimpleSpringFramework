import sys
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationType, AnnotationName


def ConfigDirectories(*directories):
    """
    添加配置文件目录，仅作用在类上
    :param directories:
    :return:
    """
    config_path_attr = AnnotationType.get_annotation_attr(AnnotationName.CONFIG_PATH)

    def decorator(cls):
        if not hasattr(cls, config_path_attr):
            setattr(cls, config_path_attr, directories)
            return cls

        # 追加多个配置目录
        base_config_path = getattr(cls, config_path_attr)
        base_config_path = base_config_path + directories
        setattr(cls, config_path_attr, base_config_path)
        return cls

    return decorator


def ComponentScan(*base_packages):
    """
    扫描模块，仅作用在类上
    :param base_packages:
    :return:
    """

    def decorator(cls):
        component_scan_attr = AnnotationType.get_annotation_attr(AnnotationName.COMPONENT_SCAN)

        if not hasattr(cls, component_scan_attr):
            setattr(cls, component_scan_attr, base_packages)
            return cls

        # 追加多个配置目录
        base_packages_new = getattr(cls, component_scan_attr)
        base_packages_new = base_packages + base_packages_new
        setattr(cls, component_scan_attr, base_packages_new)
        return cls

    return decorator


def Component(cls):
    """
    标记管理类, 默认单例，仅作用在类上
    :param cls:
    :return:
    """
    component_attr = AnnotationType.get_annotation_attr(AnnotationName.COMPONENT)
    setattr(cls, component_attr, True)

    scope_attr = AnnotationType.get_annotation_attr(AnnotationName.SCOPE)
    if not hasattr(cls, scope_attr):
        setattr(cls, scope_attr, "singleton")

    order_attr = AnnotationType.get_annotation_attr(AnnotationName.ORDER)
    if not hasattr(cls, order_attr):
        setattr(cls, order_attr, sys.maxsize)

    return cls


def Order(order_num):
    def decorator(target):
        order_attr = AnnotationType.get_annotation_attr(AnnotationName.ORDER)
        setattr(target, order_attr, order_num)
        return target

    return decorator


def Scope(scope_type):
    def decorator(cls):
        scope_attr = AnnotationType.get_annotation_attr(AnnotationName.SCOPE)
        setattr(cls, scope_attr, scope_type)
        return cls

    return decorator
