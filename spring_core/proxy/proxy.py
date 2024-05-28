"""

https://blog.csdn.net/wangmx1993328/article/details/108164388

"""
from pySimpleSpringFramework.spring_aop.framework.autoproxy.advice import MethodBeforeAdvice, MethodAfterAdvice, \
    MethodAfterReturningAdvice, MethodThrowingAdvice, MethodAroundAdvice
from pySimpleSpringFramework.spring_aop.framework.autoproxy.joinPoint import ProceedJoinPoint, JoinPoint
from pySimpleSpringFramework.spring_aop.framework.autoproxy.returnObject import ReturnObject
from pySimpleSpringFramework.spring_core.log import log
from pySimpleSpringFramework.spring_core.util.commonUtils import get_class_dot_method_name


class DynamicProxy:
    def __init__(self, target):
        self._target = target
        self.__before_advices = []
        self.__after_advices = []
        self.__returning_value_advices = []
        self.__throwing_advices = []
        self.__around_advices = []

    def __reduce__(self):
        return self.__class__, (self._target,)

    @staticmethod
    def __is_aspect_in_advices(join_point, advices):
        do_bean = join_point.target
        do_method = join_point.method

        for advice in advices:
            target_bean, target_methods = advice.get_target()
            if do_bean == target_bean and do_method in target_methods:
                return True
        return False

    @staticmethod
    def __is_aspect_in_advice(join_point, advice):
        do_bean = join_point.target
        do_method = join_point.method

        target_bean, target_methods = advice.get_target()
        return do_bean == target_bean and do_method in target_methods

    def get_target(self):
        return self._target

    def add_advice(self, advice):
        if advice is None:
            return

        # print(advice.__class__)
        if advice.__class__ == MethodBeforeAdvice:
            self.__before_advices.append(advice)
        if advice.__class__ == MethodAfterAdvice:
            self.__after_advices.append(advice)
        if advice.__class__ == MethodAfterReturningAdvice:
            self.__returning_value_advices.append(advice)
        if advice.__class__ == MethodThrowingAdvice:
            self.__throwing_advices.append(advice)
        if advice.__class__ == MethodAroundAdvice:
            self.__around_advices.append(advice)

    def __do_before(self, join_point):
        for advice in self.__before_advices:
            if not self.__is_aspect_in_advice(join_point, advice):
                continue
            advice.before(join_point)

    def __do_after(self, join_point):
        for advice in self.__after_advices:
            if not self.__is_aspect_in_advice(join_point, advice):
                continue
            advice.after(join_point)

    def __do_after_returning(self, join_point, return_object):
        for advice in self.__returning_value_advices:
            if not self.__is_aspect_in_advice(join_point, advice):
                continue
            advice.after_returning(join_point, return_object)

    def __do_after_throwing(self, join_point, ex):
        if len(self.__throwing_advices) == 0:
            raise ex
        for advice in self.__throwing_advices:
            if not self.__is_aspect_in_advice(join_point, advice):
                continue
            advice.after_throwing(join_point, ex)

    @staticmethod
    def __do_real_method(join_point):
        return_object = ReturnObject()
        return_value = join_point.method(*join_point.args, **join_point.kwargs)
        return_object.set_return_object(return_value)
        return return_object

    def __do_around(self, join_point):
        # 没有环绕方法要执行
        if len(self.__around_advices) == 0 or not self.__is_aspect_in_advices(join_point, self.__around_advices):
            return self.__do_real_method(join_point)

        # 有环绕方法要执行
        # 获取调用链
        head_proceed_join_point = self.__create_recursion_chain(join_point)
        # 执行调用链
        return_value = self.__do_recursion(head_proceed_join_point)

        return_object = ReturnObject().set_return_object(return_value)
        return return_object

    def __create_recursion_chain(self, join_point):
        """
        生成递归调用链
        :param join_point:
        :return:
        """
        head_proceed_join_point = ProceedJoinPoint(join_point)
        proceed_join_point = head_proceed_join_point
        for advice in self.__around_advices:
            # 判断当前 advice 是否要执行
            if not self.__is_aspect_in_advice(join_point, advice):
                continue
            next_proceed_join_point = ProceedJoinPoint(JoinPoint(advice, advice.around, proceed_join_point))

            proceed_join_point.set_next_proceed_join_point(next_proceed_join_point)
            proceed_join_point = next_proceed_join_point

        return head_proceed_join_point

    def __do_recursion(self, proceed_join_point):
        """
        递归调用
        :param proceed_join_point:
        :return:
        """
        next_proceed_join_point = proceed_join_point.next_proceed_join_point
        if proceed_join_point.next_proceed_join_point is not None:
            result = self.__do_recursion(next_proceed_join_point)
            return result

        result = proceed_join_point.proceed()
        return result

    def __getattr__(self, attr):
        obj = getattr(self._target, attr)
        # 如果是属性
        if not callable(obj):
            return obj

        # 如果是函数
        def wrapper(*args, **kwargs):
            real_method = obj
            join_point = JoinPoint(self._target, real_method, *args, **kwargs)
            return_object = ReturnObject()

            try:
                self.__do_before(join_point)

                return_object = self.__do_around(join_point)

                self.__do_after(join_point)
            except Exception as ex:
                log.error(str(ex))
                self.__do_after_throwing(join_point, ex)
            finally:
                self.__do_after_returning(join_point, return_object)

            return return_object.return_value

        return wrapper

    def __setattr__(self, name, value):
        if name == "_target":
            super().__setattr__(name, value)
        else:
            setattr(self._target, name, value)
