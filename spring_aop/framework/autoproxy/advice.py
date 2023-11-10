class Advice:
    def __init__(self):
        # [{类实例 : [方法列表]}]
        self._advice_target = None

    def set_advice_target(self, advice_target):
        self._advice_target = advice_target

    def get_target(self):
        return self._advice_target.target_bean, self._advice_target.target_methods

    def _do_aspect_method(self, join_point, *arg):
        # 切入逻辑
        advice_method = self._advice_target.advice_method
        advice_method(join_point, *arg)

    def _do_around_aspect_method(self, proceed_join_point, *arg):
        # 切入逻辑
        advice_method = self._advice_target.advice_method
        return_value = advice_method(proceed_join_point, *arg)
        return return_value


class MethodBeforeAdvice(Advice):
    def before(self, join_point):
        self._do_aspect_method(join_point)


class MethodAfterAdvice(Advice):
    def after(self, join_point):
        self._do_aspect_method(join_point)


class MethodAfterReturningAdvice(Advice):
    def after_returning(self, join_point, return_object):
        self._do_aspect_method(join_point, return_object)


class MethodThrowingAdvice(Advice):
    def after_throwing(self, join_point, ex):
        self._do_aspect_method(join_point, ex)


class MethodAroundAdvice(Advice):
    def around(self, process_join_point):
        return self._do_around_aspect_method(process_join_point)
