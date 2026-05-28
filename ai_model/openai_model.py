import time

import openai
from openai import OpenAI
from ai_model.model import Model
from utils.log_utils import log
from book.content import ContentType


class OpenAiModel(Model):

    # 初始化模型
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def request_model(self, prompt: str):
        """
        请求模型的接口
        返回两个值：1、翻译之后的文本 2、True False表示翻译是否成功
        给3次连接模型的机会，超过三次抛出异常
        :param prompt:
        :return:
        """
        count = 0
        while count < 3:
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=(
                        {'role': 'user', 'content': prompt},
                    )
                )
                log.info(f'模型调用成功！当前使用模型：{self.model}')
                return resp.choices[0].message.content.strip(), True
            except openai.RateLimitError as e:
                count += 1
                if count < 3:
                    # 输出一个警告，休眠10秒，然后继续调用模型api
                    log.warning('连接模型失败，10秒后将重新连接')
                    time.sleep(10)
                else:
                    log.exception('已经连续调用API接口3次了，不能再继续，请检查网')
            except Exception as e:
                log.error(e)
                return '', False
        return '', False

    # def make_prompt(self, content, target_language):
    #     if content.content_type == ContentType.TEXT and isinstance(content.original, str):
    #         return f'请翻译成{target_language}: {content.original}'
    #     if content.content_type == ContentType.TABLE:
    #         return f'请翻译成{target_language}，每个元素之间用逗号隔开，以非MarkDown的表格形式返回：\n {content.get_original_to_string()}'



