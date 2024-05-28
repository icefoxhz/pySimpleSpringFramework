import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
from pySimpleSpringFramework.spring_core.log import log


def default_callback_function(future):
    future.result()


class ExecutorTaskManager:
    def __init__(self):
        self.__app_environment = None
        self._process_pool = None
        self._thread_pool = None
        self._core_num = 2

    @property
    def core_num(self):
        return self._core_num

    def set_environment(self, applicationEnvironment):
        self.__app_environment = applicationEnvironment

    def after_init(self):
        pool_size = self.__app_environment.get("task.execution.pool.max_size", False)
        self._core_num = multiprocessing.cpu_count() if pool_size is None else pool_size
        self.init_pool()

    def init_pool(self):
        if self._process_pool is None:
            self._create_process_pool()
        if self._thread_pool is None:
            self._create_thread_pool()

    def _create_process_pool(self):
        self._process_pool = ProcessPoolExecutor(max_workers=self._core_num)

    def _create_thread_pool(self):
        self._thread_pool = ThreadPoolExecutor(max_workers=self._core_num * 2)

    def shutdown(self):
        try:
            if self._process_pool is not None:
                self._process_pool.shutdown()

            if self._thread_pool is not None:
                self._thread_pool.shutdown()
        except:
            pass
        finally:
            self._process_pool = None
            self._thread_pool = None

    def wait_completed(self):
        self.shutdown()

    def wait_completed_and_shutdown(self):
        self.shutdown()

    @staticmethod
    def waitUntilComplete(futures):
        wait(futures)
        return all(future.done() for future in futures)

    def submit(self, task_function, use_process, callback_function, *args, **kwargs):
        if callback_function is None:
            callback_function = default_callback_function

        pool = self._process_pool if use_process else self._thread_pool
        if pool is None:
            log.error("当前池已经关闭，无法使用！请重新初始化！")
            return None

        future = pool.submit(task_function, *args, **kwargs)
        future.add_done_callback(callback_function)
        return future
