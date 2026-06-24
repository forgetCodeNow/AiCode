from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

from book.content import ContentType, Content


class Model:

    def create_llm(self):
        print('初始化大语言模型的对象')

    @staticmethod
    def make_prompt():
        """
        创建提示模版
        :return:
        """
        system_template = """
        你是一位翻译专家，精通人类各国语言，
        输入的是：{source_language}语言，翻译后输出的是：{target_language}语言
        """
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template('{text}')

        return ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])


        # if content.content_type == ContentType.TEXT and isinstance(content.original, str):
        #     return f'请翻译成{target_language}，（直接给我翻译后的文本，不需要有其他非翻译的文本回答）: {content.original}'
        # if content.content_type == ContentType.TABLE:
        #     return f'请翻译成{target_language}，每个元素之间用逗号隔开，以非MarkDown的表格形式返回：\n {content.get_original_to_string()}'
