import unittest

from pySimpleSpringFramework.spring_core.applicationStarter import ApplicationStarter
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component, ComponentScan, \
    ConfigDirectories


@Component
@ComponentScan("../../pySimpleSpringFramework/spring_test/test_beans")
@ConfigDirectories("../../config")
class MyServiceApplicationTest(ApplicationStarter):
    def main(self, app):
        pass


class TestAddition(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        service_app = MyServiceApplicationTest()
        service_app.run()
        app = service_app.application_context

        self.loginService = app.get_bean("loginService")
        self.assertNotEqual(self.loginService, None)

        self.queryService = app.get_bean("queryService")
        self.assertNotEqual(self.queryService, None)

        self.a = app.get_bean("a")
        self.b = app.get_bean("b")
        self.c = app.get_bean("c")
        self.assertNotEqual(self.a, None)
        self.assertNotEqual(self.b, None)
        self.assertNotEqual(self.c, None)

        print(">>>> setUp <<<<")

    def tearDown(self) -> None:
        super().tearDown()
        # del app
        print(">>>> tearDown <<<<")

    def test_ioc(self):
        self.assertNotEqual(self.a, self.queryService.a)
        self.assertEqual(self.a.b, self.queryService.a.b)
        self.assertEqual(self.b, self.queryService.b)
        self.assertEqual(self.c, self.queryService.c)
        self.assertEqual(self.c.a, self.queryService.c.a)

    def test_aop(self):
        print("-------------------------------------------  test_aop ----------------------------------------------\n")
        self.a.my_print()
        """
        >>>>>>>>> aspectBefore2 = >
        this is a
        >>>>>>>>> aspectAfter2 = >
        >>>>>>>>> aspectAfterReturning2 = >

        """
        print("--------------------------------------------------------------------------------------------\n")

        self.b.my_print()
        """
        >>>>>>>>> aspectBefore2 = >
        >>>>>>>>> aspectBefore1 = >
        >>>>>>>>>  around before aspectAround1
        call b' my_print
        >>>>>>>>>  around after aspectAround1
        >>>>>>>>> aspectAfter2 = >
        >>>>>>>>> aspectAfter1 = >
        >>>>>>>>> aspectAfterReturning2 = >
        """
        print("--------------------------------------------------------------------------------------------\n")

        self.c.my_print()
        """
        >>>>>>>>> aspectBefore2 = >
        this is c
        >>>>>>>>> aspectAfter2 = >
        >>>>>>>>> aspectAfterReturning2 = >
        """
        print("--------------------------------------------------------------------------------------------\n")

        self.a.f1()
        """
        this is a's f1
        """
        print("--------------------------------------------------------------------------------------------\n")

        self.b.f1()
        """
        >>>>>>>>> aspectBefore1 = >
        call b' f1
        >>>>>>>>> aspectAfter1 = >
        """
        print("--------------------------------------------------------------------------------------------\n")

        result = self.b.get_result()
        """
        >>>>>>>>> aspectBefore1 = >
        >>>>>>>>>  around before aspectAround2
        >>>>>>>>>  around before aspectAround1
        call b's get_result
        >>>>>>>>>  around after aspectAround1
        >>>>>>>>>  around after aspectAround2
        >>>>>>>>> aspectAfter1 = >
        >>>>>>>>> aspectAfterReturning2 = >
        """
        print("result = ", result)
        """
        result =  11
        """
        print("--------------------------------------------------------------------------------------------\n")

        self.queryService.throw_test()
        """
        >>>>>>>>> aop2.aspectAfterThrowing1 = >  division by zero
        >>>>>>>>> aop1.aspectAfterThrowing1 = >  division by zero
        """
        print("--------------------------------------------------------------------------------------------\n")

        self.queryService.query_test()
        """
        >>>>>>>>> aspectBefore1 = >
        ========================  do QueryService's query_test =======================
          username password
        0       hz     1234
        =============================
           id           name
        0   1             zs
        1   2             ls
        2   3             ww
        3  11            zs1
        4  22            ls1
        5  33            ww1
        6  37  john_doe11111
        7  38  john_doe11111
        8  39  john_doe11111
        9  40  john_doe11111
        =============================
        <pySimpleSpring.sysComponent.aop.proxy.DynamicProxy object at 0x00000259E734D5E0>
        <pySimpleSpring.sysComponent.aop.proxy.DynamicProxy object at 0x00000259E9DF12B0>
        <pySimpleSpring.sysComponent.aop.proxy.DynamicProxy object at 0x00000259E9DF1AF0>
        =============================

        >>>>>>>>> aspectAfter1 = >
        >>>>>>>>> aspectAfterReturning1 = >

        """
        print("--------------------------------------------------------------------------------------------\n")

    def test_aop2(self):
        self.b.get_result()

    def test_log(self):
        from pySimpleSpring.logger import log
        log.info("这是日志信息")
        log.debug("这是debug信息")
        log.warning("这是警告信息")
        log.error("这是错误日志信息")
        log.critical("这是严重级别信息", exc_info=False, stack_info=True)


if __name__ == "__main__":
    unittest.main()
