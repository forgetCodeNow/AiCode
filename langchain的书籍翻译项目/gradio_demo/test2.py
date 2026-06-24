import random
import time

import gradio as gr


def do(message, history):
    responses = [
        '你好你好你好你好你好你好你好',
        '你好吗你好吗你好吗你好吗你好吗'
    ]
    resp = random.choice(responses)
    res = ''
    for char in resp:
        res += char
        time.sleep(0.1)
        yield res

interface = gr.ChatInterface(
    fn=do
)

interface.launch(server_name='0.0.0.0', server_port=8008, share=True)