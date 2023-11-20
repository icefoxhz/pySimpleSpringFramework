import time
from pySimpleSpringFramework.spring_aop.framework.annotation.methodAnnotation import AfterReturning, Around
from pySimpleSpringFramework.spring_core.task.threadPoolManager import ThreadPoolManager
from pySimpleSpringFramework.spring_core.type.annotation.classAnnotation import Order
from pySimpleSpringFramework.spring_core.log import log


class TaskAopTemplate:
    def __init__(self):
        self._threadPoolManager = None

    def set_thread_pool(self, threadPoolManager: ThreadPoolManager):
        self._threadPoolManager = threadPoolManager

    # 待动态添加Pointcut表达式
    def aspectPointcutRun(self):
        pass

    def aspectPointcutNewThreadPool(self):
        pass

    # Around 需要自己手动调用，不会主动调用。正好这里用
    @Around(["aspectPointcutRun"])
    def aspectRun(self, proceed_join_point):
        # self._threadPoolManager.wait_all_completed()
        future = self._threadPoolManager.submit_task(proceed_join_point.proceed)
        return future

    @Around(["aspectPointcutNewThreadPool"])
    def aspectNewThreadPool(self, proceed_join_point):
        # 等待前面的任务结束，并关闭
        self._threadPoolManager.shutdown()

        log.info("========= 线程池任务开始 =========")

        start_time = time.time()
        result = proceed_join_point.proceed()

        # 等待本次任务结束，并关闭
        self._threadPoolManager.shutdown()
        end_time = time.time()
        # 计算代码执行时间
        log.info("======== 线程池任务完成，耗时: {:.2f}秒".format(end_time - start_time))

        return result
