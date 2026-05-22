import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

# 第一轮对话
response = client.responses.create(
    model='qwen3.6-flash',
    instructions='你是一位数学导师，可以回答各种数学的问题',
    input='解释下导数的定义',
    tools=[{"type": "code_interpreter"}],
)

res = client.responses.retrieve(response.id)

# print(res.output[0].content[0].text)


# 第二轮对话
response = client.responses.create(
    # 
    previous_response_id=response.id,
    model='qwen3.6-flash',
    input='那偏导呢',
)



res = client.responses.retrieve(response.id)

print(res.output)

#  获取所有上下文列表
#
# input_list = client.responses.input_items.list(response.id)
# result = [{'role':data.role, 'text':data.content[0].text} for data in input_list.data]
#
# for data in result:
#     print(data['role'], data['text'])