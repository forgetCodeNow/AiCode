"""
05_创建文档向量空间和检索器.py

功能说明：
    本脚本演示如何使用 LangChain + Chroma 向量数据库构建 RAG（检索增强生成）系统。
    流程：文档切分 -> 向量化存储 -> 相似性检索 -> 拼接上下文 -> LLM 生成回答。

依赖：
    pip install langchain langchain-chroma langchain-openai langchain-core

环境变量：
    DASHSCOPE_API_KEY  - 阿里百炼 DashScope API 密钥
    LANGCHAIN_API_KEY  - LangSmith 追踪密钥（可选）
"""

import os

# LangChain Chroma：轻量级本地向量数据库，用于存储和检索文档向量
from langchain_chroma import Chroma

# LangChain 核心组件：消息、提示词模板、链式调用工具
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

# OpenAI 兼容接口：ChatOpenAI 用于对话生成，OpenAIEmbeddings 用于文本向量化
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Document：LangChain 的文档数据结构，包含文本内容（page_content）和元数据（metadata）
from langchain_core.documents import Document

# ============================================================
# LangSmith 监控配置
# 用于追踪和调试链式调用，可在 LangSmith 面板中查看执行日志
# ============================================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "langchain-demo"

# ============================================================
# 1. 创建大语言模型实例
# 使用阿里百炼 DashScope 的 OpenAI 兼容端点，模型为 qwen3.7-plus
# ============================================================
model = ChatOpenAI(
    model="qwen3.7-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# ============================================================
# 2. 准备测试文档数据
# 每篇文档由 page_content（正文）和 metadata（来源标签）组成
# ============================================================
documents = [
    Document(
        page_content="狗是伟大的伴侣，以其忠诚和友好而闻名。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
    Document(
        page_content="猫是独立的宠物，通常喜欢自己的空间。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
    Document(
        page_content="金鱼是初学者的流行宠物，需要相对简单的护理。",
        metadata={"source": "鱼类宠物文档"},
    ),
    Document(
        page_content="鹦鹉是聪明的鸟类，能够模仿人类的语言。",
        metadata={"source": "鸟类宠物文档"},
    ),
    Document(
        page_content="兔子是社交动物，需要足够的空间跳跃。",
        metadata={"source": "哺乳动物宠物文档"},
    ),
]

# ============================================================
# 3. 创建文本向量化模型（Embeddings）
# 使用阿里百炼的 text-embedding-v1 模型将文本转换为向量
# 注意：必须设置 tiktoken_enabled=False 和 check_embedding_ctx_length=False，
#       否则 OpenAIEmbeddings 会尝试从 HuggingFace 下载模型配置导致连接超时
# ============================================================
embeddings = OpenAIEmbeddings(
    model="text-embedding-v1",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    tiktoken_enabled=False,          # 关闭 OpenAI 的 tiktoken 分词器校验（DashScope 不支持）
    check_embedding_ctx_length=False,  # 关闭 HuggingFace 模型配置获取（避免连接超时）
)

# ============================================================
# 4. 创建向量数据库（Chroma）
# 将文档通过 embeddings 转换为向量后存入 Chroma 内存数据库
# ============================================================
vector_store = Chroma.from_documents(documents, embedding=embeddings)

# 可选：查看相似度查询结果，分数越低表示相似度越高
# print(vector_store.similarity_search_with_score('傻狗'))

# ============================================================
# 5. 创建检索器（Retriever）
# 将向量数据库的相似性搜索封装为 Runnable，方便接入链式调用
# ============================================================
retriever = RunnableLambda(vector_store.similarity_search)

# 测试检索器：输入查询词，返回最相关的文档列表
# print(retriever.batch(['傻狗', '鸟']))

# ============================================================
# 6. 构建提示词模板（Prompt Template）
# 将用户问题和检索到的上下文拼接成完整的提示词，引导 LLM 基于上下文回答
# ============================================================
message = """
使用提供的上下文回答这个问题：
{question}
上下文：
{context}
"""

prompt_template = ChatPromptTemplate.from_messages([("human", message)])

# ============================================================
# 7. 构建 RAG 链（Chain）
# 流程：用户问题 -> 同时传给检索器（获取上下文）和提示词模板 -> LLM 生成回答
# RunnablePassthrough() 将原始问题原样传递，确保 prompt 中 {question} 有值
# ============================================================
chain = {"question": RunnablePassthrough(), "context": retriever} | prompt_template | model

# ============================================================
# 8. 执行链式调用并打印结果
# ============================================================
resp = chain.invoke("狗是什么东西")

print(resp.content)
