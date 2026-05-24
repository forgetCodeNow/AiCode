from openai import OpenAI
from ai_model.model import Model


class OpenAiModel(Model):

    # 初始化模型
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)


    def request_model(self, prompt: str):
        return self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'user', 'content': prompt},
            ]
        )