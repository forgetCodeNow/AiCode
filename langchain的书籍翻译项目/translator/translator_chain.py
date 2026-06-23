from ai_model.model import Model
from book.content import Content


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
        pass