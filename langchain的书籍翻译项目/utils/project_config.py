from yaml import safe_load

from utils.argumentUtils import ArgumentUtils
from utils.log_utils import log


class ProjectConfig:
    """
    统一处理整个项目的配置，整个项目的配置对象设置为单例模式
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProjectConfig, cls).__new__(cls)
            cls._instance._args = None
            cls._instance._config = None
        return cls._instance

    def initialize(self):
        """
        初始化所有的项目配置
        :return:
        """

        # 命令行参数 配置的初始化
        if self._args is None:
            arg_utils = ArgumentUtils()
            self._args = arg_utils.parser_args()
            log.info(f'命令行参数:{self._args}')

        # YAML文件 配置的初始化： 如果YAML中的配置和命令行参数冲突，以命令行参数为准
        if self._config is None:
            with open(self._args.config, 'r') as f:
                config = safe_load(f)

            # 用非空的命令行参数覆盖 YAML 配置
            overridden_config = {
                key: value for key, value in vars(self._args).items()
                if value is not None and value != ""
            }

            config.update(overridden_config)
            self._config = config

    def __getattr__(self, item):
        if self._config and item in self._config:
            return self._config[item]
        else:
            raise AttributeError(f"'{item}' object has no attribute '{item}'")


if __name__ == '__main__':
    test = ProjectConfig()
    test.initialize()
    print(test.model_name)
