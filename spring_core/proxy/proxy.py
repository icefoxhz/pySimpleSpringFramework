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
        # 预构建 wrapper 缓存: method_name -> wrapper 闭包（避免每次访问重新绑定方法+新建闭包）
        object.__setattr__(self, '_DynamicProxy__wrapper_cache', {})
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
            object.__setattr__(self, '_DynamicProxy__wrapper_cache', {})
            object.__setattr__(self, '_DynamicProxy__compiled_dirty', False)
            return

        compiled = {}
        wrapper_cache = {}
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
                chain._around_steps = _build_around_runner(ard, getattr(target, name))
            compiled[name] = chain

            # 预构建 wrapper（避免每次访问时重新 getattr 绑定方法 + 新建闭包）
            real_method = getattr(target, name)
            if callable(real_method):
                wrapper_cache[name] = _make_wrapper(
                    target, real_method, b, a_, r, t, chain._around_steps
                )

        object.__setattr__(self, '_DynamicProxy__compiled', compiled)
        object.__setattr__(self, '_DynamicProxy__wrapper_cache', wrapper_cache)
        object.__setattr__(self, '_DynamicProxy__compiled_dirty', False)

    # ------------------------------------------------------------------ #
    # 运行时分发                                                            #
    # ------------------------------------------------------------------ #
    def __getattr__(self, attr):
        # 1) 惰性编译（兼容外部未调用 compile() 的场景）
        if self.__compiled_dirty:
            self.compile()

        # 2) 命中预构建 wrapper（AOP 方法）：O(1) 返回，零绑定、零闭包分配
        wrapper = self.__wrapper_cache.get(attr)
        if wrapper is not None:
            return wrapper

        # 3) 非 AOP 属性直通 target
        try:
            return getattr(self._target, attr)
        except AttributeError:
            raise

    # ------------------------------------------------------------------ #
    # 核心执行（静态，避免 self 闭包）                                       #
    # ------------------------------------------------------------------ #
    @staticmethod
    def _invoke(target, real_method,
                before, after, after_returning, after_throwing,
                around_runner, args, kwargs):
        jp = JoinPoint(target, real_method, *args, **kwargs)
        ro = ReturnObject()
        ex_holder = None

        try:
            # before
            for advice in before:
                advice.before(jp)

            # 主调用
            if around_runner:
                rv = around_runner(args, kwargs)
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


def _make_wrapper(target, real_method, before, after, after_returning, after_throwing, around_runner):
    """预构建 wrapper 闭包：运行时只做一次 dict 查找，不再绑定方法/新建闭包。"""
    def wrapper(*args, **kwargs):
        return DynamicProxy._invoke(
            target, real_method,
            before, after, after_returning, after_throwing,
            around_runner, args, kwargs
        )
    return wrapper


def _build_around_runner(steps, real_method):
    """
    预构建 around 执行链（compile 时一次性装配）：
    返回 runner(args, kwargs)，运行时零闭包分配。
    steps[0] 是最外层（最先跑），最内层落到 real_method。
    """
    if not steps:
        return ()

    def leaf(args, kwargs):
        return real_method(*args, **kwargs)

    runner = leaf
    # 从最内层 step 开始向外装配
    for i in range(len(steps) - 1, -1, -1):
        step = steps[i]
        inner = runner

        def make_run(a=step, nxt=inner):
            def run(args, kwargs):
                pjp = _ProceedJoinPoint(lambda: nxt(args, kwargs), args=args, kwargs=kwargs)
                return a.around(pjp)
            return run

        runner = make_run()
    return runner
