from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, as_completed
import queue
from pySimpleSpringFramework.spring_core.log import log


class ThreadPoolManager:
    def __init__(self):
        self._max_workers = None
        self.__executor = None
        self.__futures = []

    def after_init(self):
        self._createThreadPoolExecutor()

    def set_environment(self, environment):
        self._max_workers = environment.get(key="task.execution.pool.max_size", raise_ex=False)

    def _createThreadPoolExecutor(self):
        if self.__executor is None:
            # log.info("====== 创建新的线程池 ======")
            self.__executor = ThreadPoolExecutor(max_workers=self._max_workers)

    def submit_task(self, task, *args, **kwargs):
        # 提交任务到线程池
        # log.info("提交任务: " + str(task))
        future = self.__executor.submit(task, *args, **kwargs)
        self.__futures.append(future)
        return future

    @property
    def max_workers(self):
        return getattr(self.__executor, '_max_workers', None)

    @property
    def current_running_tasks(self):
        work_queue = getattr(self.__executor, '_work_queue', None)
        current_running_tasks = work_queue.qsize() if work_queue is not None else 0
        return current_running_tasks

    def wait_for_all_completed(self, clear_futures=True):
        completed_futures, unfinished_futures = wait(self.__futures, return_when=ALL_COMPLETED)
        if clear_futures:
            del self.__futures
            self.__futures = []

    def wait_completed(self, completed_size=4):
        while True:
            futures = list(as_completed(self.__futures))
            if len(futures) % completed_size == 0:
                for future in futures:
                    self.__futures = self.__futures.remove(future)
                break
        return futures

    def shutdown(self, clear_futures=True):
        if self.__executor is not None:
            # log.info("====== 关闭当前线程池{} ======".format(",且先等待所有任务完成" if clear_futures else ""))
            # 关闭线程池
            self.__executor.shutdown(wait=True)
            self.__executor = None
            if clear_futures:
                del self.__futures
                self.__futures = []

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
