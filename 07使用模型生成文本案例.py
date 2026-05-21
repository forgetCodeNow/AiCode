import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

res = client.chat.completions.create(
    model="qwen3.6-flash",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ],
    max_tokens=200,
)
print(res.choices[0].message.content)
print(res)