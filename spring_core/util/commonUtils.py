import inspect

from pySimpleSpringFramework.spring_core.type.attrType import AttrJudgeType


def is_custom_function(member):
    """
    自定义函数，用于过滤掉系统方法
    :param member:
    :return:
    """
    return inspect.isfunction(member) or (inspect.ismethod(member))


def is_instance(instance, attr_judge_name):
    """
    系统的 isinstance，只要加载路径不一样, 同一个类也会判断成False
    :param instance:
    :param attr_judge_name:
    :return:
    """
    attr_name = AttrJudgeType.get_attr_name(attr_judge_name)
    return hasattr(instance, attr_name)


def get_bean_name_by_class_name(cls_name):
    return cls_name[0].lower() + cls_name[1:]


def get_bean_name_by_class(cls):
    return get_bean_name_by_class_name(cls.__name__)


def get_class_name_from_method(method):
    return method.__qualname__.split('.')[0]


def get_class_dot_method_name(method):
    class_name = get_class_name_from_method(method)
    method_name = method.__name__
    return class_name + "." + method_name


def get_init_propertiesEx(instance):
    """
    获取实例中定义的属性
    :return:  显示属性名 =>   [实际属性名, 属性值] , 因为 self.__xx 这种的实际属性名是这样的： _NewClass__xx ，而不是 __xx
    """
    private_prefix = "_" + instance.__class__.__name__
    property_dict = {}

    # print("Properties defined in __init__:")
    for attr in dir(instance):
        if not callable(getattr(instance, attr)) and not attr.startswith("__") and not attr.endswith("__"):
            attr_name = attr if not attr.startswith(private_prefix) else attr.replace(private_prefix, "")
            property_dict.setdefault(attr_name, getattr(instance, attr))
    return property_dict


def get_nested_value(dot_key, my_dict, raise_ex=True) -> any or None:
    """
    1. properties 文件的key 就是像 a.b.c 这样的，所以先直接查下  my_dict["a.b.c"]
    2. 根据字符串获取字典中的值，比如  a.b.c 返回 my_dict['a']['b']['c']
    :param dot_key:
    :param my_dict:
    :param raise_ex:
    :return:
    """
    if type(my_dict) != dict:
        return None

    # properties 文件的key 就是像 a.b.c 这样的，所以先直接查下
    value = my_dict.get(dot_key, None)
    if value is not None:
        return value

    keys = dot_key.split('.')  # 将输入字符串分割为键列表
    value = my_dict

    for key in keys:
        if key in value:
            value = value[key]
        else:
            if raise_ex:
                raise KeyError("配置文件中没有找到key: [ {} ]".format(dot_key))
            return None

    return value
