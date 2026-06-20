

import os

# LangChain Chroma：轻量级本地向量数据库，用于存储和检索文档向量
from langchain_chroma import Chroma

# LangChain 核心组件：消息、提示词模板、链式调用工具
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults

# OpenAI 兼容接口：ChatOpenAI 用于对话生成，OpenAIEmbeddings 用于文本向量化
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# Document：LangChain 的文档数据结构，包含文本内容（page_content）和元数据（metadata）
from langchain_core.documents import Document
from langgraph.prebuilt import chat_agent_executor

# ============================================================
# LangSmith 监控配置
# 用于追踪和调试链式调用，可在 LangSmith 面板中查看执行日志
# ============================================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "langchain-demo"
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")

# ============================================================
# 1. 创建大语言模型实例
# 使用阿里百炼 DashScope 的 OpenAI 兼容端点，模型为 qwen3.7-plus
# ============================================================
model = ChatOpenAI(
    model="qwen-max",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


# # 没有代理和工具情况下
# result = model.invoke([HumanMessage(content='今天深圳天气怎么样')])
# print(result.content)

# 使用langchain内置的tavily搜索引擎工具
# 使用Tavily需要到官方获取到apikey
search = TavilySearchResults(max_results=2)     # 最多返回两个结果
# print(search.invoke('今天深圳天气怎么样'))

# 模型绑定search工具
tools = [search]
model_with_tavily = model.bind_tools(tools)

# 模型可以自动推理：是否需要调用工具去完成用户的答案
# resp = model_with_tavily.invoke([HumanMessage(content='今天深圳天气怎么样')])
# print(f'Model_resp: {resp.content}')
# print(f'Tools_resp: {resp.tool_calls}')


# 创建agent

agent_executor = chat_agent_executor.create_tool_calling_executor(model, tools)

resp1 = agent_executor.invoke({'messages': [HumanMessage(content='今天深圳的天气怎么样')]})
print(resp1['messages'])

resp2 = agent_executor.invoke({'messages': [HumanMessage(content='中国的首都在哪里')]})
print(resp2['messages'])
