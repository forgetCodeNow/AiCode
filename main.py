import os

from ai_model.glm_model import OpenAiGlmModel
from ai_model.openai_model import OpenAiModel
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


    # 初始化模型对象
    if args.model_type == 'OpenAiModel':
        client = OpenAiModel(model_name, api_key, base_url)
    else:
        client = OpenAiGlmModel(model_name, api_key, base_url)

    result = client.request_model('who are you?')
    print(result)