import os

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

# ============================================================
# LangSmith 监控配置
# 用于追踪和调试链式调用，可在 LangSmith 面板中查看执行日志
# ============================================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "langchain-demo"

# ============================================================
# 1. 创建大语言模型实例
# 使用阿里百炼 DashScope 的 OpenAI 兼容端点，模型为 deepseek-v4-pro
# ============================================================
model = ChatOpenAI(
    model="deepseek-v4-pro",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# ============================================================
# 2. 定义提示词模板
# - system: 设定角色和行为，language 为动态参数，支持多语言
# - MessagesPlaceholder: 占位符，接收每轮对话的用户消息和历史消息
#   variable_name 必须与 RunnableWithMessageHistory 的 input_messages_key 一致
# ============================================================
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个聊天助手，用{language}跟我聊天"),
    MessagesPlaceholder(variable_name="input_messages"),
])

# ============================================================
# 3. 构建 Chain
# 将 prompt 模板和模型通过管道符连接，组成一个可运行的链
# ============================================================
chain = prompt_template | model

# ============================================================
# 4. 会话历史管理
# store: 字典存储所有用户的聊天记录，以 session_id 为 key 区分不同会话
# get_session_history: 根据 session_id 获取或创建对应的 ChatMessageHistory
# ============================================================
store = {}

def get_session_history(session_id):
    """获取指定会话的历史记录，不存在则创建新的"""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# ============================================================
# 5. 包装 RunnableWithMessageHistory
# 在 chain 外层包裹消息历史管理能力：
# - input_messages_key: 指定输入中承载用户消息的 key
# - 每次 invoke 时，自动将历史消息 + 当前输入拼接后传给 chain
#   调用结束后自动将本轮对话写入 store
# ============================================================
do_message = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input_messages",
)

# ============================================================
# 6. 定义会话配置
# session_id 用于区分不同用户/会话，存储和读取各自的聊天记录
# ============================================================
config = {"configurable": {"session_id": "l1"}}

# ============================================================
# 7. 模拟多轮对话
# ============================================================

# 第1轮：用户自我介绍
resp = do_message.invoke(
    input={
        "input_messages": [HumanMessage(content="你好！我是老大")],
        "language": "中文",
    },
    config=config,
)
print(resp.content)

# 第2轮：验证模型是否记住了上下文（依赖历史消息）
resp2 = do_message.invoke(
    input={
        "input_messages": [HumanMessage(content="我叫什么?")],
        "language": "中文",
    },
    config=config,
)
print(resp2.content)

# 第3轮-流式输出
for resp in do_message.stream(
    input={
        "input_messages": [HumanMessage(content="用我的名字讲一个小笑话")],
        "language": "中文",
    },
    config=config,
):
    print(resp.content,end='-')
