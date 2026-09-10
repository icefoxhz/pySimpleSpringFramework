from pySimpleSpringFramework.spring_aop.framework.annotation.classAnnotation import Aspect
from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import Pointcut, AfterThrowing
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Component, Order


@Component
@Aspect
@Order(1)
class Aop2:
    @Pointcut({"execution": ["*.*"]})
    def aspectPointcut5(self):
        pass

    @AfterThrowing(["aspectPointcut5"])
    def aspectAfterThrowing1(self, joinPoint, ex):
        print(">>>>>>>>> aop2.aspectAfterThrowing1 = > ", joinPoint.target, joinPoint.method, joinPoint.args,
              joinPoint.kwargs, str(ex))
