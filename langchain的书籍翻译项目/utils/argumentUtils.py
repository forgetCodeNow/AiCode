import argparse


class ArgumentUtils:
    """命令行参数解析工具类

    用于处理书籍自动翻译器的命令行参数配置，提供统一的参数管理接口。
    """

    def __init__(self):
        """初始化参数解析器

        创建ArgumentParser实例并定义所有支持的命令行参数。
        """
        # 创建参数解析器实例，设置程序描述信息
        self.parser = argparse.ArgumentParser(description='书籍自动翻译器')

        # 添加--config参数，用于指定配置文件路径
        # type=str: 参数类型为字符串
        # default='config.yaml': 默认值为config.yaml
        # help: 参数的帮助说明，用户运行--help时显示
        self.parser.add_argument(
            '--config',
            type=str,
            default='config.yaml',
            help='项目的整体配置文件'
        )
        # self.parser.add_argument('--model_type', type=str, required=True, default='OpenAiModel',      # required=True 表述命令行执行程序必须写--model_type
        #                          choices=['OpenAiModel', 'GLMModel'], help='选择大模型')
        self.parser.add_argument('--model_type', type=str, default='OpenAiModel',
                                 choices=['OpenAiModel', 'GLMModel'], help='选择大模型')
        self.parser.add_argument('--model_name', type=str, default='', help='OpenAi中使用的模型')
        # self.parser.add_argument('--openai_api_key', type=str, default='', help='OpenAi中的api_key')
        self.parser.add_argument('--inoput_file', type=str, default='', help='需要翻译的书籍的文件路径')
        self.parser.add_argument('--source_language', type=str, default='', help='翻译前的语言')
        self.parser.add_argument('--target_language', type=str, default='', help='翻译后的语言')
        self.parser.add_argument('--outpur_format', type=str, default='', help='翻译后的文件格式')
        self.parser.add_argument('--base_url', type=str, default='https://api.deepseek.com/v1',
                                 help='API访问地址')

    def parser_args(self):
        args = self.parser.parse_args()
        # if args.model_type == 'OpenAiModel' and not args.openai_model and not args.openai_api_key:
        #     self.parser.error('OpenAiModel模型必须搭配openai_model和openai_api_key')

        return args
