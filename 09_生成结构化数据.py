import os
from typing import List

from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_experimental.tabular_synthetic_data.prompts import SYNTHETIC_FEW_SHOT_PREFIX, SYNTHETIC_FEW_SHOT_SUFFIX
from pydantic import BaseModel

# ============================================================
# LangSmith 监控配置
# ============================================================
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = "langchain-demo"

# ============================================================
# 1. 创建大语言模型实例
# ============================================================
model = ChatOpenAI(
    model='deepseek-v4-flash',
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# 2. 定义数据模型
class MedicalBilling(BaseModel):
    patient_id: int
    patient_name: str
    diagnosis_code: str
    procedure_code: str
    total_charge: float
    insurance_claim_amount: float


# 用外层列表模型，一次调用生成多条
class MedicalBillingList(BaseModel):
    """List of medical billing records."""
    records: List[MedicalBilling]


# 3. 样本数据
examples = [
    {
        "example": "Patient ID: 123456, Patient Name: 张伟, Diagnosis Code: J20.9, Procedure Code: 99203, Total Charge: , Insurance Claim Amount: "
    },
    {
        "example": "Patient ID: 789012, Patient Name: 王兴鹏, Diagnosis Code: M54.5, Procedure Code: 99213, Total Charge: , Insurance Claim Amount: "
    },
    {
        "example": "Patient ID: 345678, Patient Name: 刘晓达, Diagnosis Code: E11.9, Procedure Code: 99214, Total Charge: , Insurance Claim Amount: "
    },
]

# 4. 提示模板
openai_template = PromptTemplate(input_variables=['example'], template="{example}")

prompt_template = FewShotPromptTemplate(
    prefix=SYNTHETIC_FEW_SHOT_PREFIX,
    suffix=SYNTHETIC_FEW_SHOT_SUFFIX,
    examples=examples,
    example_prompt=openai_template,
    input_variables=['subject', 'extra']
)

# 5. 绑定外层列表工具（一次调用生成全部）
model_with_tools = model.bind_tools([MedicalBillingList])

# 6. 生成
prompt_text = prompt_template.format(
    subject='医疗账单',
    extra='名字都是两个字的，保险索赔金额控制在总费用的50%-80%。请一次性生成10条不同的记录。'
)

response = model_with_tools.invoke(prompt_text)

if response.tool_calls:
    tool_call = response.tool_calls[0]
    result_list = MedicalBillingList(**tool_call['args'])
    for i, billing in enumerate(result_list.records, 1):
        print(f"--- 第 {i} 条 ---")
        print(billing)
        print()
else:
    print("未返回 tool_calls，响应内容：", response.content)
