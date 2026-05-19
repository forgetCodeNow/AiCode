import os
from openai import OpenAI
from tiktoken import model

# 确保没有代理干扰
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

# 查看API_KEY
print(os.getenv('DASHSCOPE_API_KEY'))

# 连接百炼API
client = OpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)


res = client.embeddings.create(
    input='hello',
    model='text-embedding-v3'
)

# 测试是否有数据返回
print(True if res else False)

embedding = res.data[0].embedding
print(len(embedding))
