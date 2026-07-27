from langchain_openai import ChatOpenAI
from zai import ZhipuAiClient

from sql_graph.env_utils import ZHIPU_API_KEY

client = ZhipuAiClient(api_key=ZHIPU_API_KEY)

llm = ChatOpenAI(
    model='glm.4.7',
    api_key=ZHIPU_API_KEY,
    base_url='https://open.bigmodel.cn/api/paas/v4/'
)