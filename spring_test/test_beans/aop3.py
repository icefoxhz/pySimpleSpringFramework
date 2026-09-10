from pySimpleSpringFramework.spring_aop.framework.annotation.classAnnotation import Aspect
from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import Pointcut, Around
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component, Order


@Component
@Aspect
@Order(2)
class Aop3:
    @Pointcut({"execution": ["B.*"]})
    def aspectPointcutAround1(self):
        pass

    @Around(["aspectPointcutAround1"])
    def aspectAround1(self, proceed_join_point):
        print(">>>>>>>  around before aspectAround1")
        result = proceed_join_point.proceed()
        print(">>>>>>>  around after aspectAround1")
        return result


@Component
@Aspect
@Order(1)
class Aop4:
    @Pointcut({"execution": ["B.get_result"]})
    def aspectPointcutAround2(self):
        pass

    @Around(["aspectPointcutAround2"])
    def aspectAround2(self, proceed_join_point):
        print(">>>>>>>  around before aspectAround2")
        result = proceed_join_point.proceed()
        print(">>>>>>>  around after aspectAround2")
        return result
