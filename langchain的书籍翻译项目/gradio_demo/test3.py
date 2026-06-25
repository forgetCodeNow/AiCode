import random
import time

import gradio as gr
from gradio import Blocks


def save(message, history):
    """接收用户输入，追加一条 user 消息到聊天历史，并清空输入框。"""
    history.append({"role": "user", "content": message})
    return "", history


def do(history):
    """模拟流式回复：随机选一句，逐字追加到 assistant 消息的 content 中。"""
    responses = [
        '你好你好你好你好你好你好你好',
        '你好吗你好吗你好吗你好吗你好吗'
    ]
    resp = random.choice(responses)
    # 先插入一条空的 assistant 消息作为占位，后续逐字填充
    history.append({"role": "assistant", "content": ""})
    for char in resp:
        history[-1]["content"] += char
        time.sleep(0.1)  # 模拟打字延迟
        yield history  # 使用 yield 实现流式输出


with Blocks(title='AI机器人') as blocks:
    # 聊天显示区
    chatbot = gr.Chatbot(height=350, placeholder='AI机器人')
    # 用户输入框，container=False 去掉默认外框
    msg = gr.Text(placeholder='请输出你的问题', container=False)

    # 提交事件链：save 先记录用户消息 → do 再生成流式回复
    msg.submit(
        fn=save, inputs=[msg, chatbot], outputs=[msg, chatbot], queue=False
    ).then(
        fn=do, inputs=chatbot, outputs=chatbot
    )

# 启用队列以支持流式输出
blocks.queue()
blocks.launch(server_name='0.0.0.0', server_port=8008, share=True)
