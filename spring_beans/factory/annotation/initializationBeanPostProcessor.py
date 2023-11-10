from pySimpleSpringFramework.spring_beans.factory.annotation.abstractInitializationBeanPostProcessor import \
    AbstractInitializationBeanPostProcessor


class InitializationBeanPostProcessor(AbstractInitializationBeanPostProcessor):
    def post_process_before_initialization(self, bean_name, bean) -> object or None:
        for method_name in self._before_method_names:
            if self._invoke(bean_name, bean, method_name):
                return bean
        return bean

    def post_process_after_initialization(self, bean_name, bean) -> object or None:
        for method_name in self._after_method_names:
            if self._invoke(bean_name, bean, method_name):
                return bean
        return bean

