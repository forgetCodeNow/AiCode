import os

from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator
from utils.project_config import ProjectConfig

if __name__ == '__main__':
    # 初始化项目整体配置
    config = ProjectConfig()
    config.initialize()

    # 初始化大语言模型
    if config.model_type == 'OpenAIModel':
        api_key: str = os.getenv('DEEPSEEK_API_KEY')
        model = OpenAiModel(config.model_name, api_key, config.base_url)

    # 初始化一个翻译器
    translator = PDFTranslator(model)

    translator.book_translation(pdf_file_path=config.input_file, source_language=config.source_language, target_language=config.target_language, out_file_format=config.output_format)