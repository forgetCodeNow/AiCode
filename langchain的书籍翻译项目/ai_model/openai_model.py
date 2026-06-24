import os
import time

import openai
from langchain_openai import ChatOpenAI
from openai import OpenAI
from ai_model.model import Model
from utils.log_utils import log
from book.content import ContentType


class OpenAiModel(Model):

    # 初始化模型
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def create_llm(self):
        """
        初始化openai的大语言模型对象
        :return:
        """
        model = ChatOpenAI(model=self.model, api_key=self.api_key, base_url=self.base_url)
        return model
