from langchain_core.prompts import PromptTemplate

from langchain_demo.my_llm import llm

prompt_template = PromptTemplate.from_template('帮我生成一个简短的，关于{topic}的短文')

res = prompt_template.invoke({'topic': '相声'})


chain = prompt_template | llm

resp = chain.invoke({'topic': '相声'})