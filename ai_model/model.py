from book.content import ContentType


class Model:

    def request_model(self, prompt):
        print('发送请求，调用ai模型')


    def make_prompt(self, content, target_language):
        if content.content_type == ContentType.TEXT and isinstance(content.original, str):
            return f'请翻译成{target_language}，（直接给我翻译后的文本，不需要有其他非翻译的文本回答）: {content.original}'
        if content.content_type == ContentType.TABLE:
            return f'请翻译成{target_language}，每个元素之间用逗号隔开，以非MarkDown的表格形式返回：\n {content.get_original_to_string()}'
