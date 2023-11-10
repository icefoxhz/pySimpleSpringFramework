from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import AfterReturning, Around
from pySimpleSpringFramework.spring_core.task.threadPoolManager import ThreadPoolManager
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Order


class TaskAopTemplate:
    def __init__(self):
        self._threadPoolManager = None

    def set_thread_pool(self, threadPoolManager: ThreadPoolManager):
        self._threadPoolManager = threadPoolManager

    # 待动态添加Pointcut表达式
    def aspectPointcutRun(self):
        pass

    # Around 需要自己手动调用，不会主动调用。正好这里用
    @Around(["aspectPointcutRun"])
    def aspectExecute(self, proceed_join_point):
        result = self._threadPoolManager.submit_task(proceed_join_point.proceed)
        return result


