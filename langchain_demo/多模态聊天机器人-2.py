from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory

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

res1 = chain_with_message_history.invoke({'input': '我是浩浩'}, config={'configurable': {'session_id': "hh123"}})
print(res1)

res2 = chain_with_message_history.invoke({'input': '我是谁'}, config={'configurable': {'session_id': "hh123"}})
print(res2)
