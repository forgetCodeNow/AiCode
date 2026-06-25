import os

import gradio as gr

from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator
from utils.project_config import ProjectConfig


def translation(file_path, source_language, target_language):
    translator = init_translator()
    output_file = translator.book_translation(pdf_file_path=file_path, source_language=source_language, target_language=target_language)
    return output_file

def init_translator():
    # 初始化项目整体配置
    config = ProjectConfig()
    config.initialize()

    # 初始化大语言模型
    if config.model_type == 'OpenAIModel':
        api_key: str = os.getenv('DEEPSEEK_API_KEY')
        model = OpenAiModel(config.model_name, api_key, config.base_url)

    # 初始化一个翻译器
    translator = PDFTranslator(model)
    return translator

def run_gradio():
    instance = gr.Interface(
        fn=translation,
        title='书籍自动翻译 V2.0',
        inputs=[
            gr.File(label='上错PDF书籍文件'),
            gr.Textbox(label='源语言', value='English'),
            gr.Textbox(label='目标语言', value='Chinese'),
        ],
        outputs=[
            gr.File(label='下载翻译之后的文件')
        ]
    )

    instance.launch(server_name='0.0.0.0', server_port=8008)




if __name__ == '__main__':
    init_translator()
    run_gradio()