from argparse import ArgumentParser

from yaml import safe_load


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
            arg_utils = ArgumentParser()
            self._args = arg_utils.parse_args()

        # YAML文件 配置的初始化： 如果YAML中的配置和命令行参数冲突，以命令行参数为准
        if self._config is None:
            with open(self._args.config, 'r') as f:
                config = safe_load(f)

            overridden_config = {  # 所有冲突的配置，都取命令行参数
                key: value for key, value in vars(self._args).items() if key in config and value is not None
            }

            config.update(overridden_config)  # 把命令的参数覆盖config文件
            self._config = config

    def __getattr__(self, item):
        # 当访问当前对象实例的属性时 自动调用该魔法方法
        # 外部可以直接访问config文件里面的参数
        if self._config and item in self._config:
            return self._cofnig[item]
        else:
            raise AttributeError(f"'{item}' object has no attribute '{item}'")


if __name__ == '__main__':
    test = ProjectConfig()
    test.initialize()
    print(test.model_name)
