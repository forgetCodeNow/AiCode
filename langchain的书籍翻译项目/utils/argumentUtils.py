import argparse


class ArgumentUtils:
    """命令行参数解析工具类

    用于处理书籍自动翻译器的命令行参数配置，提供统一的参数管理接口。
    """

    def __init__(self):
        """初始化参数解析器

        创建ArgumentParser实例并定义所有支持的命令行参数。
        """
        self.parser = argparse.ArgumentParser(description="书籍自动翻译器")

        self.parser.add_argument("--config", type=str, default="config.yaml",
                                 help="项目的整体配置文件")
        self.parser.add_argument("--model_type", type=str, default="OpenAIModel",
                                 choices=["OpenAIModel", "GLMModel"], help="选择大模型")
        self.parser.add_argument("--model_name", type=str, default="", help="OpenAi中使用的模型")
        self.parser.add_argument("--api_key", type=str, default="", help="API密钥")
        self.parser.add_argument("--input_file", type=str, default="", help="需要翻译的书籍的文件路径")
        self.parser.add_argument("--source_language", type=str, default="", help="翻译前的语言")
        self.parser.add_argument("--target_language", type=str, default="", help="翻译后的语言")
        self.parser.add_argument("--output_format", type=str, default="", help="翻译后的文件格式")
        self.parser.add_argument("--base_url", type=str, default="https://api.deepseek.com/v1", help="API访问地址")

    def parser_args(self):
        args = self.parser.parse_args()
        return args
