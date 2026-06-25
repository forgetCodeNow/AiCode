from typing import Optional

from openai.types.audio import translation

from translator.file_writer import FileWriter
from translator.translator_chain import TranslatorChain
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
        self.langchain = TranslatorChain(model)
        self.writer = FileWriter(self.book)

    def book_translation(self, pdf_file_path: str, source_language: str, out_file_format: str = 'PDF', target_language: str = '中文', out_file_path: str = None, pages: Optional[int] = None):
        """
        翻译指定的一本书
        :param pdf_file_path:
        :param source_language:
        :param out_file_format:
        :param target_language:
        :param out_file_path:
        :param pages: 需要翻译的页数，默认原本翻译
        :return:
        """

        self.book = pdf_parser(pdf_file_path, pages)

        # 把真实数据传入FileWriter类
        self.writer.book = self.book

        for page_index, page in enumerate(self.book.pages):
            for content_index, content in enumerate(page.contents):
                # 开始翻译每一个content
                translation_text, status = self.langchain.run(content, source_language, target_language)

                log.debug(f'大语言模型翻译后的内容：\n{translation_text}')
                # 把翻译后的文本存放到content里面
                self.book.pages[page_index].contents[content_index].set_translation(translation_text, status)

        # 调用写入模块将翻译后的数据写入out_file_format指定文件
        return self.writer.write_to_file(out_file_path, out_file_format)



