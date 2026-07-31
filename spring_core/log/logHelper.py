import logging
import os
import sys
import colorlog
from logging.handlers import RotatingFileHandler
from datetime import datetime

# ---------- 全局配置 ----------
cur_path = os.getcwd()
log_path = os.path.join(cur_path, 'logs')
if not os.path.exists(log_path):
    os.mkdir(log_path)

log_colors_config = {
    'DEBUG': 'white',
    'INFO': 'cyan',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

default_formats = {
    'color_format': '%(log_color)s%(asctime)s-%(levelname)s-[日志信息]: %(message)s',
    'log_format': '%(asctime)s-%(levelname)s-[日志信息]: %(message)s'
}

# ---------- 日志类 ----------
class HandleLog:
    _loggers = {}  # 缓存已创建的 logger 对象，key 为 log_name

    def __init__(self, log_name=None):
        if log_name is None:
            log_name = "sysLog"
        self.log_name = log_name

        if log_name not in HandleLog._loggers:
            logger = self._create_logger(log_name)
            HandleLog._loggers[log_name] = logger

        self.__logger = HandleLog._loggers[log_name]

    def _create_logger(self, log_name):
        # 使用独立名称，避免与根记录器冲突
        logger = logging.getLogger(f"custom_{log_name}")
        logger.setLevel(logging.DEBUG)

        # ⭐ 关键修复：禁止日志传播到根 Logger，避免重复打印
        logger.propagate = False

        # 防止重复添加（由于缓存机制，此判断其实多余，但保留安全）
        if logger.handlers:
            return logger

        now_time = datetime.now().strftime('%Y-%m-%d')
        all_log_path = os.path.join(log_path, f"{log_name}_{now_time}_all.log")
        error_log_path = os.path.join(log_path, f"{log_name}_{now_time}_error.log")

        # ----- 文件 Handler（所有级别） -----
        all_handler = RotatingFileHandler(
            all_log_path,
            maxBytes=10 * 1024 * 1024,
            encoding='utf-8',
            backupCount=5
        )
        all_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(default_formats["log_format"])
        all_handler.setFormatter(file_formatter)

        # ----- 文件 Handler（仅 ERROR 及以上） -----
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=10 * 1024 * 1024,
            encoding='utf-8',
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        # ----- 控制台 Handler（输出到 stdout） -----
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        color_formatter = colorlog.ColoredFormatter(
            default_formats["color_format"],
            log_colors=log_colors_config
        )
        console_handler.setFormatter(color_formatter)

        # 添加所有 Handler
        logger.addHandler(all_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)

        return logger

    def _log(self, level_func, message, *args, **kwargs):
        if isinstance(message, list):
            for msg in message:
                level_func(str(msg), *args, **kwargs)
        else:
            level_func(str(message), *args, **kwargs)

    # ----- 对外接口 -----
    def debug(self, message, *args, **kwargs):
        self._log(self.__logger.debug, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._log(self.__logger.info, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self._log(self.__logger.warning, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._log(self.__logger.error, message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self._log(self.__logger.critical, message, *args, **kwargs)


# ---------- 使用示例 ----------
if __name__ == '__main__':
    log = HandleLog()
    log.info("这是日志信息")
    log.debug("这是debug信息")
    log.warning("这是警告信息")
    log.error("这是错误日志信息", exc_info=True)
    log.critical("这是严重级别信息")

    # 测试列表输入
    log.info(["列表消息1", "列表消息2"])