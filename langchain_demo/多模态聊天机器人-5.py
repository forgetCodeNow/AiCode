from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core import chat_history
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnablePassthrough
import gradio as gr
from rich import theme

from langchain_demo.my_llm import llm

# 1、提示词模版
prompt = ChatPromptTemplate.from_messages(
    [
        ('system', '{system_message}'),
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        ('human', '{input}')
    ]
)

# '你是「灵犀」，一个专业的多模态智能助手。你能同时理解文本、图像、音频、视频和常见办公文档，并能在不同模态之间进行交叉分析与推理。'

chain = prompt | llm


# 2、存储聊天记录： （内存，关系型数据库或redis数据库）
def get_session_id(session_id: str):
    """从关系型数据库中的历史聊天消息中，返回当前session_id的所有历史消息"""
    return SQLChatMessageHistory(
        session_id=session_id,
        connection='sqlite:///chat_history.db'
    )


# 3、创建带历史记录功能的处理链
chain_with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_id,
    input_messages_key='input',
    history_messages_key='chat_history',
)


# 4、剪辑和摘要上下文，历史记录：保留最近的前2条消息，
def summarize_messages(current_input):
    """剪辑和摘要上下文，历史记录"""
    session_id = current_input['config']['configurable']['session_id']
    if not session_id:
        raise ValueError('必须通过config参数提供session_id')

    # 获取当前会话ID的所有历史聊天记录
    chat_history = get_session_id(session_id)
    stored_messages = chat_history.messages

    if len(stored_messages) <= 2:  # 保留最近2条消息的阈值
        return {
            'original_messages': stored_messages,
            'summary': None,
        }

    # 剪辑消息列表
    last_two_messages = stored_messages[-2:]
    messages_to_summarize = stored_messages[:-2]

    summarization_prompt = ChatPromptTemplate.from_messages([
        ('system', '请将一下对话历史消息压缩为一条保留关键消息的摘要消息'),
        ('placeholder', '{chat_history}'),
        ('human', '请生成包含上述对话核心内容的摘要信息，保留重要事实和决策')
    ]
    )

    summarization_chain = summarization_prompt | llm
    # 生成摘要
    summary_messages = summarization_chain.invoke({'chat_history': messages_to_summarize})

    return {
        'original_messages': last_two_messages,
        'summary': summary_messages,
    }


# 最终的链
# RunnablePassthrough 默认会把输出数据原样传递到下游，而.assign()方法允许保留原始输入的同时，通过指定键值对（messages_summarized=summarize_messages）向输入的字典中添加新字段
final_chain = RunnablePassthrough.assign(messages_summarized=summarize_messages) | RunnablePassthrough.assign(
    input=lambda x: x['input'],
    chat_history=lambda x: x['messages_summarized']['original_messages'],
    system_message=lambda
        x: f'你是「灵犀」，一个专业的多模态智能助手。摘要：{x['messages_summarized']['summary'] if x['messages_summarized'].get('summary') else '无摘要'}',
) | chain_with_message_history

# res1 = final_chain.invoke({'input': '我是浩浩', 'config': {'configurable': {'session_id': "hh123"}}},
#                           config={'configurable': {'session_id': "hh123"}})
# print(res1)
#
# res2 = final_chain.invoke({'input': '我是谁', 'config': {'configurable': {'session_id': "hh123"}}},
#                           config={'configurable': {'session_id': "hh123"}})
# print(res2)
#
# res3 = final_chain.invoke({'input': '用我的名字写一首诗', 'config': {'configurable': {'session_id': "hh123"}}},
#                           config={'configurable': {'session_id': "hh123"}})
# print(res3)

# res4 = final_chain.invoke({'input': '猜一下我姓什么，全名叫什么', 'config': {'configurable': {'session_id': "hh123"}}},
#                           config={'configurable': {'session_id': "hh123"}})
# print(res4)

# web界面的核心函数
def add_message(chat_history, user_message):
    if user_message:
        chat_history.append({'role': 'user', 'content': user_message})
    return chat_history, ''

def execute_chain(chat_history):
    input = chat_history[-1]
    if isinstance(input.get('content'), list):
        input_text = input['content'][0]['text']
    else:
        input_text = input.get('content', '')
    result = final_chain.invoke({'input': input_text, 'config': {'configurable': {'session_id': "hh123"}}},
                              config={'configurable': {'session_id': "hh123"}})
    chat_history.append({'role': 'assistant', 'content': result.content})
    return chat_history


# 开发聊天机器人的界面
with gr.Blocks(title='多模态聊天机器人', theme=gr.themes.Soft()) as block:

    # 聊天历史记录组件
    chatbot = gr.Chatbot(height=500, label='聊天机器人')

    with gr.Row():
        # 文字输入区域
        with gr.Column(scale=4):
            user_input = gr.Textbox(placeholder='请给机器人发送消息...', label='用户输入', max_lines=5)
            submit_btn = gr.Button(value='发送', variant='primary')

        with gr.Column(scale=1):
            audio_input = gr.Audio(sources=['microphone'], label='语音输入', type='filepath', format='wav')

    chat_msg = user_input.submit(add_message, [chatbot, user_input], [chatbot, user_input])
    chat_msg.then(execute_chain, chatbot, chatbot)
    submit_btn.click()

if __name__ == '__main__':
    block.launch()
