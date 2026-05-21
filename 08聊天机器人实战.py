import os
from openai import OpenAI

def save_context(res):
    out_res = res.choices[0].message
    print(out_res.content)

    messages.append({'role': out_res.role,'content': out_res.content})

def new_prompt(role='user', content=''):
    new_chat = {
        'role': role,
        'content': content
    }
    messages.append(new_chat)



client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你是谁？"},
    ]

# # 第一轮聊天
# res = client.chat.completions.create(
#     model="qwen3.6-flash",
#     messages=messages,
# )
#
# save_context(res)
#
# # 第二轮聊天
# new_chat ={
#         'role':'user',
#         'content':'帮我计算22*33'
#      }
#
# messages.append(new_chat)
#
# res = client.chat.completions.create(
#     model="qwen3.6-flash",
#     messages=messages,
# )
#
# save_context(res)
#
# # 第三轮聊天
# new_chat = {
#         'role':'user',
#         'content':'上一个结果除以100的结果是什么'
#      }
#
#
# messages.append(new_chat)
#
# res = client.chat.completions.create(
#     model="qwen3.6-flash",
#     messages=messages,
# )
#
# save_context(res)



# 升级无限问答
while True:
    new_content = input('输出问题(q退出）：')
    if new_content == 'q':
        break
    new_prompt(content=new_content)

    res = client.chat.completions.create(
        model="qwen3.6-flash",
        messages=messages,
    )

    save_context(res)

