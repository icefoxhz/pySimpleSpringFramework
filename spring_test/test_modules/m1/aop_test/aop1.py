from pySimpleSpringFramework.spring_aop.framework.annotation.classAnnotation import Aspect
from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import Pointcut, Before, After, \
    AfterReturning, AfterThrowing
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component, Order


# @Component
# @Aspect
# @Order(2)
class AspectTest1:
    def _test(self):
        print("1111111111")

    @Pointcut({"execution": ["*.*", "A.f1"]})
    def aspectPointcut1(self):
        pass

    @Pointcut({"execution": ["B.get_result"]})
    def aspectPointcut4(self):
        pass

    @Before(["aspectPointcut1"])
    @Order(2)
    def aspectBefore1(self, joinPoint):
        # self._test()
        print(">>>>>>>>> aspectBefore1 = > ", joinPoint.target, joinPoint.method, joinPoint.args, joinPoint.kwargs)

    @Before(["aspectPointcut1", "aspectPointcut4"])
    @Order(1)
    def aspectBefore2(self, joinPoint):
        # self._test()
        print(">>>>>>>>> aspectBefore2 = > ", joinPoint.target, joinPoint.method, joinPoint.args, joinPoint.kwargs)

    @After(["aspectPointcut1", "aspectPointcut4"])
    @Order(2)
    def aspectAfter1(self, joinPoint):
        # self._test()
        print(">>>>>>>>> aspectAfter1 = > ", joinPoint.target, joinPoint.method, joinPoint.args, joinPoint.kwargs)

    @After(["aspectPointcut4"])
    @Order(1)
    def aspectAfter2(self, joinPoint):
        # self._test()
        print(">>>>>>>>> aspectAfter2 = > ", joinPoint.target, joinPoint.method, joinPoint.args, joinPoint.kwargs)

    # @AfterReturning(["aspectPointcut1"])
    # @Order(2)
    # def aspectAfterReturning1(self, joinPoint, return_object):
    #     print(">>>>>>>>> aspectAfterReturning1 = > ", joinPoint.target, joinPoint.method, joinPoint.args,
    #           joinPoint.kwargs,
    #           return_object)
    #     print()
    #
    # @AfterReturning(["aspectPointcut2"])
    # @Order(1)
    # def aspectAfterReturning2(self, joinPoint, return_object):
    #     print(">>>>>>>>> aspectAfterReturning2 = > ", joinPoint.target, joinPoint.method, joinPoint.args,
    #           joinPoint.kwargs,
    #           return_object)
    #     print()
    #
    # @AfterReturning(["aspectPointcut4"])
    # @Order(3)
    # def aspectAfterReturning3(self, joinPoint, return_object):
    #     # new_return_value = []
    #     # for v in return_object.return_value:
    #     #     v += 1
    #     #     new_return_value.append(v)
    #     # return_object.return_value = new_return_value
    #
    #     return_object.return_value = return_object.return_value + 10
    #
    #     print(">>>>>>>>> aspectAfterReturning3 = > ", joinPoint.target, joinPoint.method, joinPoint.args,
    #           joinPoint.kwargs,
    #           return_object)
    #     print()
    #
    # @AfterThrowing(["aspectPointcut5"])
    # def aspectAfterThrowing1(self, joinPoint, ex):
    #     print(">>>>>>>>> aop1.aspectAfterThrowing1 = > ", joinPoint.target, joinPoint.method, joinPoint.args,
    #           joinPoint.kwargs,
    #           str(ex))
