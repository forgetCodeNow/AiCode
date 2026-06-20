

import os

import bs4
# LangChain Chroma：轻量级本地向量数据库，用于存储和检索文档向量
from langchain_chroma import Chroma
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.chat_message_histories import ChatMessageHistory

# LangChain 核心组件：消息、提示词模板、链式调用工具
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableWithMessageHistory

# OpenAI 兼容接口：ChatOpenAI 用于对话生成，OpenAIEmbeddings 用于文本向量化
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Document：LangChain 的文档数据结构，包含文本内容（page_content）和元数据（metadata）
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ============================================================
# LangSmith 监控配置
# 用于追踪和调试链式调用，可在 LangSmith 面板中查看执行日志
# ============================================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = "langchain-demo"

# ============================================================
# 1. 创建大语言模型实例
# ============================================================
model = ChatOpenAI(
    model=('deepseek-v4-flash'),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

embeddings = OpenAIEmbeddings(
    model="text-embedding-v4",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    chunk_size=10,
    tiktoken_enabled=False,          # 关闭 OpenAI 的 tiktoken 分词器校验（DashScope 不支持）
    check_embedding_ctx_length=False,  # 关闭 HuggingFace 模型配置获取（避免连接超时）
)

# 1、数据加载
loader = WebBaseLoader(
    web_paths=['https://lilianweng.github.io/posts/2023-06-23-agent/'],
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(class_=('post-header', 'post-title', 'post-content'))
    )
)

docs = loader.load()


# 2、大文本的切割, 每个块1000个字符，允许重叠200字符
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = splitter.split_documents(docs)

# 3、存储
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

# 4、检索器
retriever = vectorstore.as_retriever()

# 整合
# 创建一个问题的上下文检索模版
system_prompt = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer 
the question. If you don't know the answer, say that you 
don't know. Use three sentences maximum and keep the answer concise.\n

{context}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', system_prompt),
        MessagesPlaceholder('chat_history'),   # 历史记录
        ('human', '{input}')
    ]
)

# 创建chain --- 用于组合文档并生成回答
chain1 = create_stuff_documents_chain(model, prompt)

'''
注意：
一般情况下，我们构建的链（chain）直接使用输入问答记录来关联上下文。但在此案例中，查询检索器也需要对话上下文才能被理解。

解决办法：
添加一个子链(chain)，它采用最新用户问题和聊天历史，并在它引用历史信息中的任何信息时重新表述问题。这可以被简单地认为是构建一个新的“历史感知”检索器。
这个子链的目的：让检索过程融入了对话的上下文。
'''
# 创建子链，给检索器能够理解对话历史并据此形成独立问题
# 子链提示模版
contextualize_q_system_prompt = """Given a chat history and the latest user question 
which might reference context in the chat history, 
formulate a standalone question which can be understood 
without the chat history. Do NOT answer the question, 
just reformulate it if needed and otherwise return it as is."""

retriever_history_temp = ChatPromptTemplate.from_messages(
    [
        ('system', contextualize_q_system_prompt),
        MessagesPlaceholder('chat_history'),
        ('human', '{input}')
    ]
)

# 创建子链
history_chain = create_history_aware_retriever(model, retriever, retriever_history_temp)

# 保存问答的历史记录
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 创建父链：把两个子链结合
chain = create_retrieval_chain(history_chain,chain1)

result_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key='input',
    history_messages_key='chat_history',
    output_messages_key='answer',
)

# 第一轮对话
resp1 = result_chain.invoke(
    {'input': 'What is Task Decomposition?'},
    config={'configurable': {'session_id': 'zs123456'}}
)

print(resp1['answer'])

# 第二轮对话
resp2 = result_chain.invoke(
    {'input': 'What are common ways of doing it?'},
    config={'configurable': {'session_id': 'zs123456'}}
)

print(resp2['answer'])



