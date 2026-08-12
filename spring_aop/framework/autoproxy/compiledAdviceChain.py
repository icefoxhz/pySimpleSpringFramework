"""
预编译的 AOP advice 链。

DynamicProxy 在创建后调用 compile()，把 (method_name -> CompiledAdviceChain) 索引建好。
运行时 __getattr__ 直接 O(1) 查找，避免每次方法调用都遍历所有 advice + 匹配 target/method。
"""


class CompiledAdviceChain:
    """
    单个方法上的 advice 链（已过滤 + 已排序）。
    每个属性都是 tuple，元素是直接可调用的 advice 对象。
    """
    __slots__ = ('before', 'after', 'after_returning',
                 'after_throwing', 'around', '_around_steps')

    def __init__(self):
        self.before = ()
        self.after = ()
        self.after_returning = ()
        self.after_throwing = ()
        self.around = ()
        # 预构建的 around 调用链（proceed 闭包列表），仅在 around 非空时构建
        self._around_steps = ()

    @property
    def empty(self):
        return not (self.before or self.after or
                    self.after_returning or self.after_throwing or
                    self.around)


class _ProceedJoinPoint:
    """
    轻量级 ProceedJoinPoint，仅持有 proceed 闭包。
    对外暴露 proceed() / get_args() 接口，与旧 ProceedJoinPoint 行为兼容。
    """
    __slots__ = ('_proceed', '_args', '_kwargs')

    def __init__(self, proceed_callable, args=(), kwargs=None):
        self._proceed = proceed_callable
        self._args = args
        self._kwargs = kwargs if kwargs is not None else {}

    def proceed(self):
        return self._proceed()

    def get_args(self):
        return self._args, self._kwargs
