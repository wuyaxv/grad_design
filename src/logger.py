# 用于记录日志
import logging
from datetime import datetime

# 定义不同级别对应的颜色转义码

COLOR_CODES = {
    'DEBUG': '\033[94m',  # 蓝色
    'INFO': '\033[92m',   # 绿色
    'WARNING': '\033[93m',  # 黄色
    'ERROR': '\033[91m',   # 红色
    'CRITICAL': '\033[95m'  # 紫色
}

RESET_CODE = '\033[0m'  # 重置颜色

class logger:

    def __init__(self, name="logger", description=""):
        self.logger = None
        self.do_log = True
        self.logger_name = name
        self.logger_description = description
        self.setup_logger(self.logger_name, self.logger_description)

    def setup_logger(self, name, description=""):
        formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler=None
        if not description:        # 设置是标准输出还是输出到日志文件
            handler = logging.StreamHandler()
        else:
            handler = logging.FileHandler(
                    filename=datetime.now().strftime("%Y-%m-%d_%H-%M-%S-")+description+'.log',
                    encoding="UTF-8"
                    )
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)
    
    def log_message(self, message, level='info'):
        if self.do_log:
            color_code = COLOR_CODES.get(level.upper(), '')  # 获取对应级别的颜色码
            reset_code = RESET_CODE
            
            if color_code:
                message = f"{color_code}{message}{reset_code}"  # 添加颜色转义码
            
            if level.lower() == 'debug':
                self.logger.debug(message)
            elif level.lower() == 'info':
                self.logger.info(message)
            elif level.lower() == 'warning':
                self.logger.warning(message)
            elif level.lower() == 'error':
                self.logger.error(message)
            elif level.lower() == 'critical':
                self.logger.critical(message)
            else:
                print("Invalid log level provided: {}".format(level))

"""Ssage description
You can set up your own logger, or you can simply import this file and use logger.l as your global logger. You can also redefine this logger.l and add some descriptions. Adding descriptions will cause the log information to be stored persistently in a local log file named after your description.
"""
l = logger()

