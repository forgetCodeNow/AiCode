import time

import gradio as gr


def do(text: str, propress=gr.Progress()):
    res = ''
    propress(0, desc='开始...')

    for word in propress.tqdm(text, desc='运行中'):
        time.sleep(0.25)
        res += word
    return res

interface = gr.Interface(
    fn=do,
    inputs=[
        gr.Text(label='请输入文本')
    ],
    outputs=[
        gr.Text(label='输出的结果：')
    ]
)

interface.launch(server_name='0.0.0.0', server_port=8008, share=True)