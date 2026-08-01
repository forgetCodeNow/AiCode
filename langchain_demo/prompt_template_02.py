import json

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from langchain_demo.my_llm import llm

prompt_template = PromptTemplate.from_template('帮我生成一个简短的，关于{topic}的笑话')

res = prompt_template.invoke({'topic': '相声'})

# 定义输出的schema
class TopicOutput(BaseModel):
    setup: str = Field(description='笑话的开头部分')
    punchline: str = Field(description='笑话的笑点')
    rating: int = Field(description='笑话的搞笑等级，从1-10共十个等级')

llm_with_structured_output = llm.bind_tools([TopicOutput], tool_choice='auto')


chain = prompt_template | llm_with_structured_output

resp = chain.invoke({'topic': '狗'})
print(resp.tool_calls[0]['args'])

# json格式输出
resp_json = json.dumps(resp.tool_calls[0]['args'], ensure_ascii=False)
print(resp_json)

