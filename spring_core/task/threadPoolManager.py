import concurrent.futures

from pySimpleSpringFramework.spring_core.log import log


class ThreadPoolManager:
    def __init__(self):
        self._max_workers = None
        self.__executor = None

    def set_environment(self, environment):
        self._max_workers = environment.get(key="task.execution.pool.max_size", raise_ex=False)

    def submit_task(self, task, *args, **kwargs):
        # 懒启动
        if self.__executor is None:
            log.info("====== 创建线程池 ======")
            self.__executor = concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers)

        # 提交任务到线程池
        log.info("提交任务: " + str(task))
        future = self.__executor.submit(task, *args, **kwargs)
        return future.result()

    @property
    def max_workers(self):
        return getattr(self.__executor, '_max_workers', None)

    @property
    def current_running_tasks(self):
        work_queue = getattr(self.__executor, '_work_queue', None)
        current_running_tasks = work_queue.qsize() if work_queue is not None else 0
        return current_running_tasks

    def shutdown(self):
        # 关闭线程池
        self.__executor.shutdown()


# if __name__ == "__main__":
#     def worker_function(number):
#         return number + 1
#
#     pool_manager = ThreadPoolManager()
#     # pool_manager.set_environment({})
#     pool_manager.set_environment({"task.execution.pool.max-size": 3})
#
#     print(pool_manager.max_workers)
#
#     # i = 1
#     # # 服务主循环
#     # while True:
#     #     # 模拟接收请求并处理
#     #     future = pool_manager.submit_task(worker_function, i)
#     #     result = future.result()
#     #     print("Result:", result)
#     #     i += 1
#
#     # 关闭线程池
#     pool_manager.shutdown()
