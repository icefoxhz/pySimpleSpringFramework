"""
DynamicProxy 预编译优化单元测试（纯 AOP 行为验证，不依赖数据库 / Web 环境）

覆盖:
- before / after / after_returning 触发顺序与参数
- around 链的"后添加先执行"语义
- after_throwing 异常路径
- 跨方法隔离（advice 只作用于配置的方法）
- 无 AOP 方法直通（零分配）
- 通配符 * 匹配
- after_returning 改写返回值

运行:
    python -m unittest pySimpleSpringFramework.spring_test.aop_proxy_unit_test -v
"""
import unittest

# 若环境缺 colorlog，则 stub 掉日志模块，保证本测试可在纯净环境运行
try:
    from pySimpleSpringFramework.spring_core.log import log  # noqa: F401
except ImportError:
    import sys
    import types

    _log_module = types.ModuleType("pySimpleSpringFramework.spring_core.log")

    class _StubLog:
        def debug(self, *a, **k):
            pass

        def info(self, *a, **k):
            pass

        def warning(self, *a, **k):
            pass

        def error(self, *a, **k):
            pass

    _log_module.log = _StubLog()
    sys.modules["pySimpleSpringFramework.spring_core.log"] = _log_module

from pySimpleSpringFramework.spring_aop.framework.autoproxy.advice import (
    MethodBeforeAdvice, MethodAfterAdvice,
    MethodAfterReturningAdvice, MethodThrowingAdvice, MethodAroundAdvice,
)
from pySimpleSpringFramework.spring_aop.framework.autoproxy.adviceTarget import AdviceTarget
from pySimpleSpringFramework.spring_core.proxy.proxy import DynamicProxy


def _make(advice_cls, advice_method, target_bean, target_methods):
    advice = advice_cls()
    advice.set_advice_target(AdviceTarget(advice_method, target_bean, target_methods))
    return advice


class Service:
    def __init__(self):
        self.name = "svc"

    def say_hello(self, who):
        return f"hello {who}"

    def add(self, a, b):
        return a + b

    def boom(self):
        raise RuntimeError("boom!")

    def no_aop(self):
        return "untouched"


class TestDynamicProxyBehavior(unittest.TestCase):
    def test_before_after_returning_order(self):
        log = []

        def before1(jp):
            log.append("before1")

        def before2(jp):
            log.append("before2")

        def after1(jp):
            log.append("after1")

        def ret1(jp, ro):
            log.append("ret1:" + str(ro.return_value))

        svc = Service()
        proxy = DynamicProxy(svc)
        proxy.add_advice(_make(MethodBeforeAdvice, before1, svc, ["say_hello"]))
        proxy.add_advice(_make(MethodBeforeAdvice, before2, svc, ["say_hello"]))
        proxy.add_advice(_make(MethodAfterAdvice, after1, svc, ["say_hello"]))
        proxy.add_advice(_make(MethodAfterReturningAdvice, ret1, svc, ["say_hello"]))
        proxy.compile()

        result = proxy.say_hello("Alice")
        self.assertEqual(result, "hello Alice")
        self.assertEqual(log, ["before1", "before2", "after1", "ret1:hello Alice"])

    def test_around_chain_reverse_order(self):
        log = []

        def around1(pjp):
            log.append("around1-before")
            r = pjp.proceed()
            log.append("around1-after")
            return r

        def around2(pjp):
            log.append("around2-before")
            r = pjp.proceed()
            log.append("around2-after")
            return r

        svc = Service()
        proxy = DynamicProxy(svc)
        # 添加顺序: around1, around2 → 运行时 around2 先跑（与原实现一致）
        proxy.add_advice(_make(MethodAroundAdvice, around1, svc, ["add"]))
        proxy.add_advice(_make(MethodAroundAdvice, around2, svc, ["add"]))
        proxy.compile()

        result = proxy.add(2, 3)
        self.assertEqual(result, 5)
        self.assertEqual(log, ["around2-before", "around1-before", "around1-after", "around2-after"])

    def test_throwing_path(self):
        log = []

        def before(jp):
            log.append("before")

        def after(jp):
            log.append("after")

        def throwing(jp, ex):
            log.append("throwing:" + str(ex))

        svc = Service()
        proxy = DynamicProxy(svc)
        proxy.add_advice(_make(MethodBeforeAdvice, before, svc, ["boom"]))
        proxy.add_advice(_make(MethodAfterAdvice, after, svc, ["boom"]))
        proxy.add_advice(_make(MethodThrowingAdvice, throwing, svc, ["boom"]))
        proxy.compile()

        with self.assertRaises(RuntimeError):
            proxy.boom()
        self.assertIn("before", log)
        self.assertIn("throwing:boom!", log)
        self.assertNotIn("after", log)

    def test_method_isolation(self):
        log = []

        def before(jp):
            log.append("before:" + jp.method.__name__)

        svc = Service()
        proxy = DynamicProxy(svc)
        proxy.add_advice(_make(MethodBeforeAdvice, before, svc, ["say_hello"]))
        proxy.compile()

        proxy.say_hello("x")
        proxy.add(1, 2)
        proxy.no_aop()

        self.assertEqual(log, ["before:say_hello"])

    def test_passthrough_without_aop(self):
        svc = Service()
        proxy = DynamicProxy(svc)
        proxy.compile()

        self.assertEqual(proxy.no_aop(), "untouched")
        self.assertEqual(proxy.add(1, 2), 3)
        self.assertEqual(proxy.say_hello("x"), "hello x")

    def test_wildcard_match(self):
        log = []

        def before(jp):
            log.append(jp.method.__name__)

        svc = Service()
        proxy = DynamicProxy(svc)
        proxy.add_advice(_make(MethodBeforeAdvice, before, svc, ["*"]))
        proxy.compile()

        proxy.say_hello("x")
        proxy.add(1, 2)
        proxy.no_aop()

        self.assertEqual(log, ["say_hello", "add", "no_aop"])

    def test_returning_modify_return_value(self):
        def ret(jp, ro):
            ro.return_value = ro.return_value * 100

        svc = Service()
        proxy = DynamicProxy(svc)
        proxy.add_advice(_make(MethodAfterReturningAdvice, ret, svc, ["add"]))
        proxy.compile()

        self.assertEqual(proxy.add(2, 3), 500)

    def test_lazy_compile(self):
        log = []

        def before(jp):
            log.append("before")

        svc = Service()
        proxy = DynamicProxy(svc)
        proxy.add_advice(_make(MethodBeforeAdvice, before, svc, ["add"]))
        # 不手动调用 compile()，首次访问时应惰性编译
        self.assertEqual(proxy.add(1, 2), 3)
        self.assertEqual(log, ["before"])

    def test_bound_method_target_methods(self):
        """proxyCreator 路径: AdviceTarget 的 target_methods 是绑定方法对象而非字符串"""
        log = []

        def before(jp):
            log.append(jp.method.__name__)

        svc = Service()
        advice = MethodBeforeAdvice()
        advice.set_advice_target(AdviceTarget(before, svc, [svc.say_hello]))

        proxy = DynamicProxy(svc)
        proxy.add_advice(advice)
        proxy.compile()

        proxy.say_hello("x")
        proxy.add(1, 2)
        self.assertEqual(log, ["say_hello"])

    def test_bound_method_wildcard(self):
        """proxyCreator 通配符路径: target_methods 是全部绑定方法对象的列表"""
        log = []

        def before(jp):
            log.append(jp.method.__name__)

        svc = Service()
        advice = MethodBeforeAdvice()
        advice.set_advice_target(AdviceTarget(
            before, svc,
            [getattr(svc, m) for m in ("say_hello", "add", "boom", "no_aop")]
        ))

        proxy = DynamicProxy(svc)
        proxy.add_advice(advice)
        proxy.compile()

        proxy.say_hello("x")
        proxy.add(1, 2)
        proxy.no_aop()
        self.assertEqual(log, ["say_hello", "add", "no_aop"])


if __name__ == "__main__":
    unittest.main()
