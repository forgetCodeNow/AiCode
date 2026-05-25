import sys
from loguru import logger
import os

# 获取当前项目的绝对路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(root_dir, 'logs')  # 存放项目日志目录的绝对路径

# 创建日志目录
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

LOG_FILE = 'translation.log'  # 存放日志的文件


class Logger():
    def __init__(self):
        self.log_file_path = os.path.join(log_dir, LOG_FILE)
        self.logger = logger  # 写日志的对象
        # 清空所有位置
        self.logger.remove()

        # 添加控制台输出的格式，sys.stdout输出到屏幕
        self.logger.add(sys.stdout, level='DEBUG',
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 线程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容

                        )

        # 输出到日志文件的格式，
        self.logger.add(self.log_file_path, level='INFO', encoding='utf-8',
                        format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 线程名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"  # 模块名.方法名
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )


    def get_logger(self):
        return self.logger


log = Logger()
log = log.get_logger()

if __name__ == '__main__':
    pass
    # log.debug("This is a debug message.")
    # log.info("This is an info message.")
    # log.warning('这是一个警告')
    # log.trace('xxxx')
    # print('str.pdf'['str.pdf'.rindex('.'):])
    # # @log.catch  # 整个函数自动加上try， catch。自动捕获异常，并且通过日志打印
    # def test():
    #     try:
    #         print(3/0)
    #     except ZeroDivisionError as e:
    #         pass
    #         log.error(e)
    #         log.exception(e)  # 以后常用
    # test()
