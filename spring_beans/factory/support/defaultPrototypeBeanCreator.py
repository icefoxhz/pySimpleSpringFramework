import threading


class DefaultPrototypeBeanCreator:
    __local_obj = threading.local()

    def __init__(self):
        self._bean_factory = None

    def set_bean_factory(self, bean_factory):
        self._bean_factory = bean_factory

    def get_prototype(self, bean_name) -> object or None:
        """
        获取原型bean, 递归执行set注入
        :param bean_name:
        :return:
        """
        # 用于查找原型bean之间是否存在循环依赖的问题
        if not hasattr(self.__local_obj, "prototype_name_set"):
            self.__local_obj.prototype_name_set = set()

        if self.__local_obj.prototype_name_set.__contains__(bean_name):
            raise Exception("原型bean循环引用: %s" % bean_name)

        self.__local_obj.prototype_name_set.add(bean_name)

        try:
            bean = self.__create_early_prototype_object_by_name(bean_name)
            if bean is None:
                return None

            self._bean_factory.do_init_bean(bean_name, bean)

            # 原型bean进行aop
            aop_proxy_creator = self._bean_factory.get_proxy_creator()
            target = aop_proxy_creator.create(bean_name, bean)

            return target
        finally:
            self.__local_obj.prototype_name_set.clear()

    def __create_early_prototype_object_by_name(self, name) -> object or None:
        """
        生成原型bean
        :return:
        """
        bd = self._bean_factory.get_bean_definition(name)
        if bd is None:
            return None

        instance = self._bean_factory.create_early_object_by_class(bd.cls)
        if instance is None:
            return None

        return instance
