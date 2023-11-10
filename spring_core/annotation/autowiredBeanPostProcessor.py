from pySimpleSpringFramework.spring_context.support.beanPostProcessor import BeanPostProcessor
from pySimpleSpringFramework.spring_core.type.annotationType import AnnotationName
from pySimpleSpringFramework.spring_core.type.attrType import AttrJudgeType, AttrJudgeName


class AutowiredBeanPostProcessor(BeanPostProcessor):
    def post_process_before_initialization(self, bean_name, bean) -> object or None:
        pass

    def post_process_after_initialization(self, bean_name, bean) -> object or None:
        bean_definition = self._bean_factory.get_bean_definition(bean_name)
        annotation_metadata = bean_definition.get_annotation_metadata()
        bean_metadata = bean_definition.get_bean_metadata()

        # 找到当前类的所有的注入方法和其参数
        autowiring_metadata = self.__find_autowiring_metadata(bean_metadata, annotation_metadata)
        if len(autowiring_metadata) == 0:
            return

        for method, arg_names in autowiring_metadata.items():
            arg_values = []
            for arg_name in arg_names:
                real_bean = self._bean_factory.get_bean(arg_name)
                arg_values.append(real_bean)
            # 执行注入函数
            method(bean, *arg_values)

    def __find_autowiring_metadata(self, bean_metadata, annotation_metadata):
        autowiring_metadata = {}
        methods = annotation_metadata.get_methods(AnnotationName.AUTOWIRED)
        class_name = bean_metadata.cls.__name__
        for method in methods.keys():
            method_name = method.__name__

            # 判断函数名的开头是否符合要求
            is_valid = self.is_valid_autowiring_method(class_name, method_name)
            # 不符合要求
            if not is_valid:
                raise Exception(
                    "注入方法无效，类 [ {} ], 方法 [ {} ]！方法名称应该以 set 或 _set 或 __set 开头".format(
                        class_name, method_name))
            # 获取函数的参数列表
            arg_names = bean_metadata.get_method_arg_names(method)
            autowiring_metadata[method] = arg_names
        return autowiring_metadata

    @staticmethod
    def is_valid_autowiring_method(class_name, method_name):
        """
        是否有效注入函数
        :param class_name:
        :param method_name:
        :return:
        """
        # 判断函数开头
        valid = (str(method_name).startswith("set")
                 or
                 str(method_name).startswith("_set")
                 or
                 str(method_name).startswith("_" + class_name + "__set")
                 )

        return valid


setattr(AutowiredBeanPostProcessor,
        AttrJudgeType.get_attr_name(AttrJudgeName.IS_AUTOWIRED_BEAN_POSTPROCESSOR), True)
