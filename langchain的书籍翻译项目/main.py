from ai_model.openai_model import OpenAiModel
from utils.project_config import ProjectConfig

if __name__ == '__main__':
    # 初始化项目整体配置
    config = ProjectConfig()
    config.initialize()

    # 初始化大语言模型
    if config.model_type == 'OpenAIModel':
        model = OpenAiModel(config.model_name, config.api_key, config.base_url)