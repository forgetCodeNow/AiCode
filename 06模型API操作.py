import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

models = client.models.list()
model_list = [model.id for model in models.data]

# 通过模型名字直接连接
model_info = client.models.retrieve('qwen3.6-flash')
print(model_info)