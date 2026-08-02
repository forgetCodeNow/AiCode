from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core import chat_history
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory, RunnablePassthrough

from langchain_demo.my_llm import llm

# 1、提示词模版
prompt = ChatPromptTemplate.from_messages(
    [
        ('system',
         '你是「灵犀」，一个专业的多模态智能助手。你能同时理解文本、图像、音频、视频和常见办公文档，并能在不同模态之间进行交叉分析与推理。'),
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        ('human', '{input}')
    ]
)

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

    if len(stored_messages) <= 2:   # 保留最近2条消息的阈值
        return False

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

    # 清空原来历史消息，加入摘要后的消息和最近的2条完整消息
    chat_history.clear()
    chat_history.add_message(summary_messages)
    for msg in last_two_messages:
        chat_history.add_message(msg)

    return True

# 最终的链
# RunnablePassthrough 默认会把输出数据原样传递到下游，而.assign()方法允许保留原始输入的同时，通过指定键值对（messages_summarized=summarize_messages）向输入的字典中添加新字段
# 用户输入时，字典会自带是否压缩上下文字段(messages_summarized = Ture or False)
final_chain = RunnablePassthrough.assign(messages_summarized=summarize_messages) | chain_with_message_history

res1 = final_chain.invoke({'input': '我是浩浩', 'config': {'configurable': {'session_id': "hh123"}}}, config={'configurable': {'session_id': "hh123"}})
print(res1)

res2 = final_chain.invoke({'input': '我是谁', 'config': {'configurable': {'session_id': "hh123"}}}, config={'configurable': {'session_id': "hh123"}})
print(res2)

res3 = final_chain.invoke({'input': '用我的名字写一首诗', 'config': {'configurable': {'session_id': "hh123"}}}, config={'configurable': {'session_id': "hh123"}})
print(res3)
