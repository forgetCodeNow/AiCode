import os
from utils.log_utils import log
from ai_model.glm_model import OpenAiGlmModel
from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator
from utils.argumentUtils import ArgumentUtils
from utils.loader_config import LoaderConfig

if __name__ == '__main__':

    # 启动命令中所有参数解析和验证，并返回所有参数
    args_util = ArgumentUtils()
    args = args_util.parser_args()

    # 读取配置文件(YAML)
    loader_config = LoaderConfig(args.config)
    config = loader_config.load_config()

    # 模型名字
    model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']

    # api_key
    api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']

    # base_url
    base_url = args.base_url if args.base_url else config['OpenAIModel']['base_url']

    # 获取到输入的书籍路径，如果为空就默认config里面配置的路径
    file_path: str = args.book if args.book else config['common']['book']

    # 获取到输入的输出格式后缀，如果为空就默认config里面配置的输出后缀
    out_file_format: str = args.file_format if args.file_format else config['common']['file_format']

    # 获取到输入的输出文件路径，如果为空就默认config里面配置的输出文件路径
    # out_file_path: str = args.file_format if args.file_format else config['common']['file_format']

    # 初始化模型对象
    if args.model_type == 'OpenAiModel':
        client = OpenAiModel(model_name, api_key, base_url)
        log.debug(f'成功连接{model_name}大模型')
    else:
        client = OpenAiGlmModel(model_name, api_key, base_url)

    # 创建一个翻译器
    if out_file_format.lower() == 'pdf':
        translator = PDFTranslator(client)
    else:
        pass

    # 开始翻译书籍
    translator.book_translation(file_path, out_file_format, pages=3)



