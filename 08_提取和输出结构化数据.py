import os
from typing import Optional, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import Field, BaseModel

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

# pydantic: 处理数据，验证数据， 定义数据的格式， 虚拟化和反虚拟化，类型转换等等。

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个专业的提取算法。只从未结构化文本中提取相关信息。如果你不知道要提取的属性的值，返回该属性的值为null。",
        ),
        # 请参阅有关如何使用参考记录消息历史的案例
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)


# 定义person的数据结构
class Person(BaseModel):
    """
    关于一个人的数据模型
    """
    name: Optional[str] = Field(None, description='人的名字')
    hair_color: Optional[str] = Field(None, description='头发的颜色')
    height: Optional[str] = Field(None, description='以米为单位的身高')


# 定义多结构
class ManyPerson(BaseModel):
    """
    数据模型类： 代表多个人
    """
    people: List[Person]

# with_structured_output 模型的输出是一个结构化的数据，deepseek不支持这个with_structured_output方法
# chain = {'text': RunnablePassthrough()} | prompt | model.with_structured_output(schema=ManyPerson)
model_with_tools = model.bind_tools([ManyPerson])
chain = {'text': RunnablePassthrough()} | prompt | model_with_tools

text = "马路上走来一个女生，长长的黑头发披在肩上，大概1米7左右。走在她旁边的是她的男朋友，叫：刘海；比她高10厘米。"
# text = "My name is Jeff, my hair is black and i am 6 feet tall. Anna has the same color hair as me."
resp = chain.invoke(input=text)
print(resp.tool_calls[0]['args'])
