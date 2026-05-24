from openai import OpenAI
from ai_model.model import Model


class OpenAiGlmModel(Model):

    # 初始化模型
    def __init__(self, model: str, api_key: str, glm_model_url: str):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=glm_model_url)


    def request_model(self):
        pass