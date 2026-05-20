import pandas as pd
import os
from openai import OpenAI
import tiktoken
import time


# 获取 API Key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    # 如果没有环境变量，可以直接在这里填写
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')  # 替换为你的 API Key

    if DASHSCOPE_API_KEY == os.getenv('DASHSCOPE_API_KEY'):
        raise ValueError(
            " 未找到 DASHSCOPE_API_KEY！\n"
            "请通过以下方式之一设置：\n"
            "1. 设置环境变量: set DASHSCOPE_API_KEY=sk-xxx (Windows)\n"
            "2. 或在代码中直接填写 API Key"
        )

# 阿里云百炼配置
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
EMBEDDING_MODEL = "text-embedding-v3"  # 阿里云推荐的模型（v3 比 v4 更稳定）
MAX_TOKENS = 8191
TOP_N = 1000

# 读取数据
df = pd.read_csv('datas/fine_food_reviews_1k.csv')

# 保留需要的字段
df = df[['Time', 'ProductId', 'UserId', 'Score', 'Summary', 'Text']]

df['combined'] = 'Title:' + df.Summary.str.strip() + '; Text:' + df.Text.str.strip()

print(df.combined)

# 删除缺失值
df = df.dropna()

# 创建分词器
tokenizer_name = 'cl100k_base'
tokenizer = tiktoken.get_encoding(encoding_name=tokenizer_name)

df = df.sort_values('Time')
df = df.drop('Time', axis=1, inplace=False)

# 计算每条评论的token数
df['token_count'] = df.combined.apply(lambda x: len(tokenizer.encode(x)))

# 过滤超长文本，并取TOP_N条
df = df[df.token_count <= MAX_TOKENS].tail(TOP_N)

# 连接大模型
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL,
)


def embedding_text(text, model=EMBEDDING_MODEL):

    res = client.embeddings.create(input=text, model=model)
    return res.data[0].embedding

df['embedding'] = df.combined.apply(embedding_text)

print(df.embedding)

output_file = 'datas/embedding_output_1k.csv'
df.to_csv(output_file, index=False)