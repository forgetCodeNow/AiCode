import os

from fastapi import FastAPI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes

# LangSmith 监控配置
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')  # 从环境变量读取
os.environ['LANGCHAIN_PROJECT'] = 'langchain-demo'  # 项目名称，可在 LangSmith 面板中筛选

# 1、调用大语言模型（阿里百炼 DashScope OpenAI 兼容端点）
model = ChatOpenAI(
    model='qwen-max',
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

# 2、定义提示词模版
prompt_template = ChatPromptTemplate.from_messages([
    ('system', '请把下面的内容翻译成{language}'),
    ('user', '{text}')
])

# 简单的解析响应数据
# 3、创建返回的数据
parser = StrOutputParser()

# 4、得到chain
chain = prompt_template | model | parser

# 调用chain
print(chain.invoke({'language': '英语', 'text': '今天没加班！'}))

# 把程序部署成服务
# 创建fastAPI的应用
app = FastAPI(title='langchain demo', version='0.0.1', description='langchain demo')
add_routes(
    app,
    chain,
    path='/chainDemo'
)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000)


