"""
https://blog.csdn.net/wangmx1993328/article/details/108164388

DynamicProxy 优化版：
- 启动阶段由 proxyCreator 调用 compile()，把 (method_name -> CompiledAdviceChain) 索引建好
- 运行阶段 __getattr__ O(1) 查找 chain，零反射、零全表扫描
"""
from pySimpleSpringFramework.spring_aop.framework.autoproxy.advice import MethodBeforeAdvice, MethodAfterAdvice, \
    MethodAfterReturningAdvice, MethodThrowingAdvice, MethodAroundAdvice
from pySimpleSpringFramework.spring_aop.framework.autoproxy.compiledAdviceChain import (
    CompiledAdviceChain, _ProceedJoinPoint
)
from pySimpleSpringFramework.spring_aop.framework.autoproxy.joinPoint import JoinPoint
from pySimpleSpringFramework.spring_aop.framework.autoproxy.returnObject import ReturnObject
from pySimpleSpringFramework.spring_core.log import log


class DynamicProxy:
    def __init__(self, target):
        # 直接在 object 上初始化内部状态，绕过自定义 __setattr__ 的转发逻辑
        object.__setattr__(self, '_target', target)
        # 兼容旧接口：在 compile() 之前仍可用 add_advice 累积
        object.__setattr__(self, '_DynamicProxy__before_advices', [])
        object.__setattr__(self, '_DynamicProxy__after_advices', [])
        object.__setattr__(self, '_DynamicProxy__returning_value_advices', [])
        object.__setattr__(self, '_DynamicProxy__throwing_advices', [])
        object.__setattr__(self, '_DynamicProxy__around_advices', [])
        # 预编译索引: method_name -> CompiledAdviceChain
        object.__setattr__(self, '_DynamicProxy__compiled', {})
        object.__setattr__(self, '_DynamicProxy__compiled_dirty', True)
        # 上面两个内部状态必须用 object.__setattr__ 写入，因为 DynamicProxy.__setattr__
        # 会把所有非 _target 的赋值都转发到 target，破坏内部状态。
        # 下方用 _DynamicProxy__xxx 名字别名访问。

    def __reduce__(self):
        return self.__class__, (self._target,)

    def get_target(self):
        return self._target

    # ------------------------------------------------------------------ #
    # 旧接口（保持兼容）                                                    #
    # ------------------------------------------------------------------ #
    def add_advice(self, advice):
        if advice is None:
            return
        object.__setattr__(self, '_DynamicProxy__compiled_dirty', True)
        if advice.__class__ == MethodBeforeAdvice:
            self.__before_advices.append(advice)
        elif advice.__class__ == MethodAfterAdvice:
            self.__after_advices.append(advice)
        elif advice.__class__ == MethodAfterReturningAdvice:
            self.__returning_value_advices.append(advice)
        elif advice.__class__ == MethodThrowingAdvice:
            self.__throwing_advices.append(advice)
        elif advice.__class__ == MethodAroundAdvice:
            self.__around_advices.append(advice)

    # ------------------------------------------------------------------ #
    # 预编译：把所有 advice 按 (method_name) 索引好                          #
    # ------------------------------------------------------------------ #
    def compile(self):
        """把所有 advice 索引成 (method_name -> CompiledAdviceChain)。
        proxyCreator 在所有 add_advice 之后调用一次；也可在运行时首次访问时惰性触发。"""
        target = self._target
        target_class = type(target)
        before_adv = self.__before_advices
        after_adv = self.__after_advices
        ret_adv = self.__returning_value_advices
        thr_adv = self.__throwing_advices
        around_adv = self.__around_advices

        # 没有 advice 就没有索引
        if not (before_adv or after_adv or ret_adv or thr_adv or around_adv):
            object.__setattr__(self, '_DynamicProxy__compiled', {})
            object.__setattr__(self, '_DynamicProxy__compiled_dirty', False)
            return

        compiled = {}
        # 枚举 target 上所有可被 AOP 的方法名
        for name in dir(target):
            if name.startswith('__') and name.endswith('__'):
                continue
            try:
                attr = getattr(target_class, name, None)
            except Exception:
                continue
            if attr is None or not callable(attr):
                continue

            # 过滤：只保留真正命中的 advice（不命中的不再进入 chain）
            b = tuple(a for a in before_adv if _applies(a, target, name))
            a_ = tuple(a for a in after_adv if _applies(a, target, name))
            r = tuple(a for a in ret_adv if _applies(a, target, name))
            t = tuple(a for a in thr_adv if _applies(a, target, name))
            # around 反转：原实现里最后加入的最先执行
            ard = tuple(a for a in reversed(around_adv) if _applies(a, target, name))

            if not (b or a_ or r or t or ard):
                continue

            chain = CompiledAdviceChain()
            chain.before = b
            chain.after = a_
            chain.after_returning = r
            chain.after_throwing = t
            chain.around = ard
            # 预构建 around 调用链
            if ard:
                chain._around_steps = _build_around_steps(ard)
            compiled[name] = chain

        object.__setattr__(self, '_DynamicProxy__compiled', compiled)
        object.__setattr__(self, '_DynamicProxy__compiled_dirty', False)

    # ------------------------------------------------------------------ #
    # 运行时分发                                                            #
    # ------------------------------------------------------------------ #
    def __getattr__(self, attr):
        # 1) 惰性编译（兼容外部未调用 compile() 的场景）
        if self.__compiled_dirty:
            self.compile()

        # 2) 取实际属性
        try:
            obj = getattr(self._target, attr)
        except AttributeError:
            raise

        if not callable(obj):
            return obj

        # 3) O(1) 查 chain
        chain = self.__compiled.get(attr)
        if chain is None or chain.empty:
            return obj  # 没有 AOP，直通

        # 4) 构造 wrapper（每次访问只生成一次闭包，调用本身不再生成）
        target = self._target
        real_method = obj
        before = chain.before
        after = chain.after
        after_returning = chain.after_returning
        after_throwing = chain.after_throwing
        around_steps = chain._around_steps

        def wrapper(*args, **kwargs):
            return DynamicProxy._invoke(
                target, real_method,
                before, after, after_returning, after_throwing,
                around_steps, args, kwargs
            )
        return wrapper

    # ------------------------------------------------------------------ #
    # 核心执行（静态，避免 self 闭包）                                       #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _invoke(target, real_method,
                before, after, after_returning, after_throwing,
                around_steps, args, kwargs):
        jp = JoinPoint(target, real_method, *args, **kwargs)
        ro = ReturnObject()
        ex_holder = None

        try:
            # before
            for advice in before:
                advice.before(jp)

            # 主调用
            if around_steps:
                rv = _run_around(around_steps, real_method, args, kwargs)
            else:
                rv = real_method(*args, **kwargs)

            # after（仅成功）
            for advice in after:
                advice.after(jp)
        except Exception as ex:
            log.error(str(ex))
            ex_holder = ex
            for advice in after_throwing:
                advice.after_throwing(jp, ex)
            ro.set_return_object(None)
            for advice in after_returning:
                advice.after_returning(jp, ro)
            raise
        else:
            ro.set_return_object(rv)
            for advice in after_returning:
                advice.after_returning(jp, ro)
            return ro.return_value

    def __setattr__(self, name, value):
        if name == "_target":
            object.__setattr__(self, name, value)
        else:
            setattr(self._target, name, value)


# ---------------------------------------------------------------------- #
# 模块级辅助：过滤 / 预构建 around 调用链                                 #
# ---------------------------------------------------------------------- #
def _applies(advice, target, method_name):
    """判断 advice 是否作用于 target 的 method_name 上（O(1)）
    兼容两种 target_methods 形态：
    - proxyCreator 传入的绑定方法对象 (bound method)
    - 单元测试传入的方法名字符串
    """
    target_bean, target_methods = advice.get_target()
    if target_bean is not target:
        return False
    for tm in target_methods:
        if isinstance(tm, str):
            if tm == method_name or tm == "*":
                return True
        else:
            tm_name = getattr(tm, "__name__", None)
            if tm_name == method_name:
                return True
    return False


def _build_around_steps(around_advices_reversed):
    """
    直接返回按执行顺序排列的 around advice 元组。
    真正的调用链在 _run_around 里通过闭包装配。
    """
    return tuple(around_advices_reversed)


def _run_around(steps, real_method, args, kwargs):
    """执行预构建的 around 链（无递归，无每次构造的 ProceedJoinPoint）"""
    n = len(steps)
    if n == 0:
        return real_method(*args, **kwargs)

    # 叶子：直接调用真实方法
    next_call = (lambda: real_method(*args, **kwargs))

    # 从尾到头装配闭包链：
    #   steps[0] 是最外层（最先跑）
    #   steps[n-1].proceed() 才会落到 real_method
    for i in range(n - 1, -1, -1):
        advice = steps[i]
        nxt = next_call  # 闭包捕获
        pjp = _ProceedJoinPoint(nxt, args=args, kwargs=kwargs)

        def make_call(a=advice, p=pjp):
            def call():
                return a.around(p)
            return call
        next_call = make_call()
    return next_call()
