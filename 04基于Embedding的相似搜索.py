"""
基于 Embedding 的文本语义相似度搜索脚本

功能说明:
1. 使用阿里云通义千问的 text-embedding-v3 模型生成文本向量
2. 计算查询词与数据库中所有文本的余弦相似度
3. 返回最相似的前 N 条结果
"""

# ==================== 导入必要的库 ====================
import pandas as pd  # 数据处理库
import numpy as np  # 数值计算库,用于向量运算
import ast  # 安全解析字符串格式的列表
from openai import OpenAI  # OpenAI API 客户端(兼容阿里云 DashScope)
import os  # 操作系统接口,用于读取环境变量

# ==================== 配置 API 密钥和端点 ====================
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
BASE_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

# ==================== 初始化 OpenAI 客户端 ====================
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL,
)

# ==================== 读取数据 ====================
df = pd.read_csv('datas/embedding_output_1k.csv')

# 将字符串格式的 embedding 转换为 Python 列表
df['embedding_vec'] = df['embedding'].apply(ast.literal_eval)


# ==================== Embedding 函数 ====================
def embedding_text(text, model='text-embedding-v3'):
    """
    通过阿里云通义千问的 Embedding 模型将文本转换为向量

    参数:
        text (str): 需要转换的文本
        model (str): 使用的 Embedding 模型名称,默认 'text-embedding-v3'

    返回:
        list: 文本对应的嵌入向量,通常是 1536 维的浮点数列表
    """
    resp = client.embeddings.create(input=text, model=model)
    return resp.data[0].embedding


# ==================== 余弦相似度计算函数(核心!) ====================
def cosine_distance(a, b):
    """
    计算两个向量之间的余弦相似度(Cosine Similarity)

    数学公式: cos(θ) = (A · B) / (||A|| × ||B||)

    其中:
    - A · B     : 向量 A 和 B 的点积(dot product)
    - ||A||     : 向量 A 的模(长度)
    - ||B||     : 向量 B 的模
    - θ         : 两个向量之间的夹角

    返回值范围: [-1, 1]
    - 1.0  : 完全相同(方向一致)
    - 0.0  : 正交(无关)
    - -1.0 : 完全相反(方向相反)

    为什么用余弦相似度而不是欧氏距离?
    1. 关注方向而非大小: Embedding 向量的长度可能因文本长度而异,
       但我们关心的是语义方向是否一致
    2. 对向量缩放不敏感: 如果两个向量成比例(cos=1),即使长度不同,
       也认为它们语义相同
    3. 在高维空间表现好: 对于几百到几千维的 Embedding,余弦相似度
       比欧氏距离更能准确反映语义相似性

    参数:
        a (list/array): 第一个向量,例如 query 的 embedding
        b (list/array): 第二个向量,例如数据库中某条记录的 embedding

    返回:
        float: 余弦相似度值,范围 [-1, 1],值越接近 1 表示越相似
    """
    # 分子: 计算两个向量的点积
    numerator = np.dot(a, b)

    # 分母: 计算两个向量的模(长度)的乘积
    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    # 防止除以零
    if denominator == 0:
        return 0.0

    # 返回余弦相似度值
    return numerator / denominator


# ==================== 语义搜索函数 ====================
def search_by_word(df, work_key, n_result=3, print_flag=True):
    """
    根据指定的关键词(句子),在向量空间中进行语义相似度搜索

    工作流程:
        1. 将查询词转换为 embedding 向量
        2. 计算查询向量与数据库中所有向量的余弦相似度
        3. 按相似度从高到低排序
        4. 返回最相似的前 N 条结果

    参数:
        df (DataFrame): 包含 embedding 向量的 DataFrame
        work_key (str): 搜索关键词或查询句子
        n_result (int): 返回的最相似结果数量,默认 3
        print_flag (bool): 是否打印结果到控制台,默认 True

    返回:
        Series: 包含最相似的 N 条文本内容的 Pandas Series
    """
    # 步骤1: 将查询关键词转换为 embedding 向量
    word_embedding = embedding_text(work_key)

    # 步骤2: 计算相似度
    df['similarity'] = df.embedding_vec.apply(lambda x: cosine_distance(x, word_embedding))

    # 步骤3: 排序并提取最相似的结果
    res = (
        df.sort_values('similarity', ascending=False)
        .head(n_result)
        .combined
        .str.replace('Title:', "")
        .str.replace('; Content:', ';')
    )

    # 步骤4: 打印结果(可选)
    if print_flag:
        for r in res:
            print(r)
            print()

    return res


# ==================== 主程序入口 ====================
if __name__ == '__main__':
    print('=' * 50)
    search_by_word(df, 'delicious beans', 3)

    print('=' * 50)
    search_by_word(df, 'awful', 3)
