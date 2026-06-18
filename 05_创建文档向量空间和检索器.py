import os

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
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
# 使用阿里百炼 DashScope 的 OpenAI 兼容端点，模型为 deepseek-v4-pro
# ============================================================
model = ChatOpenAI(
    model="qwen3.7-plus",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 准备测试数据 ，假设我们提供的文档数据如下：
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

embeddings = OpenAIEmbeddings(
    model="text-embedding-v4",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    tiktoken_enabled=False,          # 关闭 OpenAI 的 tiktoken 校验
)

# 实例化一个向量数据库
vector_store = Chroma.from_documents(documents, embedding=embeddings)

# # 相似度的查询：返回相似的分数， 分数越低相似度越高
# print(vector_store.similarity_search_with_score('傻狗'))

# 检索器
retriever = RunnableLambda(vector_store.similarity_search)

print(retriever.batch(['傻狗', '鸟']))

# 提示模版
message = '''
使用提供的上下文回答这个问题：
{question}
上下文：
{context}
'''

prompt_template = ChatPromptTemplate.from_messages([("human", message)])

# RunnablePassthrough允许我们将用户的问题之后再传递给prompt和Model
chain = {'question': RunnablePassthrough(), 'context': retriever} | prompt_template | model

# resp = chain.invoke('狗是什么东西')
#
# print(resp.content)