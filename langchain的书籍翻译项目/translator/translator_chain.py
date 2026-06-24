from ai_model.model import Model
from book.content import Content, ContentType
from utils.log_utils import log


class TranslatorChain:
    """
    负责调用langchain来完成文本的翻译， chain对象，可以设置成单例模式
    """
    _instance = None

    def __init__(self, model: Model):
        self.langchain = Model.make_prompt() | model.create_llm()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TranslatorChain, cls).__new__(cls)
        return cls._instance

    def run(self, content: Content, source_language: str, target_language: str):
        """
        翻译具体的文本，返回翻译之后的文本内容和翻译成功的状态
        :param content:
        :param source_language:
        :param target_language:
        :return:
        """
        result = ''

        try:
            if content.content_type == ContentType.TEXT:
                text = f'请按照要求翻译以下内容：{content.original}'
            elif content.content_type == ContentType.TABLE:
                text = f'请按照要求翻译以下内容，每个元素之间用逗号隔开，以非MarkDown的表格形式返回：{content.get_original_to_string()}'
            else:
                return result, False

            result = self.langchain.invoke({
                'source_language': source_language,
                'target_language': target_language,
                'text': text
            })

            # log.info(f'翻译后的内容：{result.content}')
        except Exception as e:
            log.exception(e)
            return result, False
        return result.content, True
