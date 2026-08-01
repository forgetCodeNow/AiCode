from langchain_openai import ChatOpenAI

from env_utils import GLM_API_KEY, GLM_BASE_URL

llm = ChatOpenAI(
    model='glm-4.7',
    api_key=GLM_API_KEY,
    base_url=GLM_BASE_URL
)