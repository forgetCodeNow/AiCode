import pandas as pd
import os
from openai import OpenAI
import tiktoken
import time

# ==================== 配置部分 ====================
# 代理配置（如果需要）
# os.environ['http_proxy'] = '127.0.0.1:7890'
# os.environ['https_proxy'] = '127.0.0.1:7890'

# 获取 API Key
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    # 如果没有环境变量，可以直接在这里填写
    DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')  # 替换为你的 API Key

    if DASHSCOPE_API_KEY == os.getenv('DASHSCOPE_API_KEY'):
        raise ValueError(
            " 未找到 DASHSCOPE_API_KEY！\n"
            "请通过以下方式之一设置：\n"
            "1. 设置环境变量: set DASHSCOPE_API_KEY=sk-xxx (Windows)\n"
            "2. 或在代码中直接填写 API Key"
        )

# 阿里云百炼配置
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
EMBEDDING_MODEL = "text-embedding-v3"  # 阿里云推荐的模型（v3 比 v4 更稳定）
MAX_TOKENS = 8191
TOP_N = 1000

print("=" * 60)
print(" Amazon 美食评论 Embedding 处理工具")
print("=" * 60)
print(f"✅ API Key 已配置")
print(f" Base URL: {BASE_URL}")
print(f"🤖 模型: {EMBEDDING_MODEL}")
print("=" * 60)

# ==================== 第一步：数据读取与预处理 ====================
print("\n📂 正在读取数据...")
df = pd.read_csv('datas/fine_food_reviews_1k.csv', index_col=0)

# 只保留需要的字段
df = df[['Time', 'ProductId', 'UserId', 'Score', 'Summary', 'Text']]

# 删除缺失值
original_count = len(df)
df = df.dropna()
if len(df) < original_count:
    print(f"⚠️  删除了 {original_count - len(df)} 条包含缺失值的记录")

# 合并摘要和正文
df['combined'] = "Title:" + df.Summary.str.strip() + "; Content:" + df.Text.str.strip()

print(f"✅ 数据预处理完成，共 {len(df)} 条有效记录")

# ==================== 第二步：Token 控制 ====================
print("\n🔢 正在计算 Token 数量...")
tokenizer_name = 'cl100k_base'
tokenizer = tiktoken.get_encoding(encoding_name=tokenizer_name)

# 按时间排序并删除 Time 列
df = df.sort_values('Time')
df.drop("Time", axis=1, inplace=True)

# 计算每条记录的 token 数
df['count_token'] = df.combined.apply(lambda x: len(tokenizer.encode(x)))

# 过滤超长文本并取最近的 TOP_N 条
before_filter = len(df)
df = df[df.count_token <= MAX_TOKENS].tail(TOP_N)

if len(df) < before_filter:
    print(f"⚠️  过滤了 {before_filter - len(df)} 条超过 {MAX_TOKENS} tokens 的记录")

print(f"✅ Token 过滤完成，最终处理 {len(df)} 条评论")

# ==================== 第三步：初始化客户端 ====================
print("\n🔌 正在初始化 OpenAI 客户端...")
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL,
)
print("✅ 客户端初始化成功")


# ==================== 第四步：生成 Embedding 向量 ====================
def embedding_text(text, model=EMBEDDING_MODEL):
    """
    通过阿里云百炼的 Embedding 模型处理文本数据

    :param text: 需要处理的文本数据
    :param model: 使用的模型名称
    :return: 嵌入向量（列表），失败返回 None
    """
    max_retries = 3  # 最大重试次数

    for attempt in range(max_retries):
        try:
            resp = client.embeddings.create(input=text, model=model)
            return resp.data[0].embedding

        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避：2s, 4s
                print(f"⚠️  API 调用失败，{wait_time}秒后重试 ({attempt + 1}/{max_retries})")
                print(f"   错误信息: {str(e)[:100]}")
                time.sleep(wait_time)
            else:
                print(f"❌ 处理失败（已重试 {max_retries} 次）: {str(e)[:100]}")
                return None


# 批量生成嵌入向量（带进度显示）
print("\n🚀 开始生成 Embedding 向量...")
print(f"   预计耗时: 约 {len(df) // 10} - {len(df) // 5} 分钟（取决于网络速度）\n")

embeddings = []
failed_count = 0
total = len(df)

for idx, text in enumerate(df['combined'], 1):
    embedding = embedding_text(text)

    if embedding is None:
        failed_count += 1
        embeddings.append(None)
    else:
        embeddings.append(embedding)

    # 每处理 50 条显示一次进度
    if idx % 50 == 0 or idx == total:
        progress = idx * 100 // total
        print(f" 进度: [{idx}/{total}] {progress}% | 失败: {failed_count} 条")

df['embedding'] = embeddings

# 删除失败的记录
if failed_count > 0:
    print(f"\n⚠️  警告: {failed_count} 条记录处理失败，将被删除")
    df_before = len(df)
    df = df.dropna(subset=['embedding'])
    print(f"   剩余记录: {len(df)} 条")

# ==================== 第五步：保存结果 ====================
output_file = 'datas/embedding_output_1k.csv'
print(f"\n 正在保存结果到: {output_file}")
df.to_csv(output_file, index=False)

# 验证结果
if len(df) > 0:
    first_embedding = df['embedding'].iloc[0]
    print(f"\n✅ 处理完成！")
    print(f"    成功处理: {len(df)} 条评论")
    print(f"    向量维度: {len(first_embedding)}")
    print(f"   💾 保存位置: {output_file}")
    print(f"\n 第一条记录的向量示例（前10个值）:")
    print(f"   {first_embedding[:10]}")
else:
    print("\n❌ 错误: 没有成功处理任何记录，请检查 API Key 和网络连接")