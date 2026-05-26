from typing import Optional

from openai.types.audio import translation

from utils.log_utils import log
from ai_model.model import Model
from ai_model.openai_model import OpenAiModel
from translator.pdf_parser import pdf_parser


class PDFTranslator:
    '''
    翻译pdf文件
    '''

    def __init__(self, model: Model):
        self.book = None
        self.model = model

    def book_translation(self, pdf_file_path: str, out_file_format: str = 'PDF', target_language: str = '中文', out_file_path: str = None, pages: Optional[int] = None):
        '''
        翻译一本书
        :param pdf_file_path:
        :param out_file_format:
        :param traget_language:
        :param out_file_path:
        :param pages: 需要翻译的页数
        :return:
        '''

        self.book = pdf_parser(pdf_file_path, pages)

        for page_index, page in enumerate(self.book.pages):
            for content_index, content in enumerate(page.contents):
                # 开始翻译每一个content
                # 1、得到翻译的prompt
                prompt = self.model.make_prompt(content, target_language)
                log.debug('大语言模型的提示信息：'+ prompt)

                # 2、调用大语言模型,得到翻译后的文本和状态
                translation_text, status = self.model.request_model(prompt)

                log.debug(f'大语言模型翻译后的文本：{translation_text}')
                # 把翻译后的文本存放到content里面
                self.book.pages[page_index].contents[content_index].set_translation(translation_text, status)



