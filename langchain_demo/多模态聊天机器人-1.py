from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory

from langchain_demo.my_llm import llm

# 1、提示词模版
prompt = ChatPromptTemplate.from_messages(
    [
        ('system', '你是「灵犀」，一个专业的多模态智能助手。你能同时理解文本、图像、音频、视频和常见办公文档，并能在不同模态之间进行交叉分析与推理。'),
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        ('human', 'input')
    ]
)

chain = prompt | llm

# 2、存储聊天记录： （内存，关系型数据库或redis数据库）
store = {}  # 用来保存历史消息，key：会话ID session_id

def get_session_id(session_id: str):
    """从内存中的历史聊天消息中，返回当前session_id的所有历史消息"""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# langchain中的四种消息类型：SystemMessage, HumanMessage, AIMessage, ToolMessage


# 3、创建带历史记录功能的处理链

chain_with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_id,
    input_messages_key='input',
    history_messages_key='chat_history',
)