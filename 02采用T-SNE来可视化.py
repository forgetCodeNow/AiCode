"""
亚马逊评论 Embedding 向量可视化脚本

功能说明:
1. 读取包含评论 Embedding 向量和评分的 CSV 文件
2. 将字符串格式的 Embedding 转换为数值向量
3. 使用 T-SNE 算法将高维向量降维到 2D 空间
4. 根据评分用不同颜色绘制散点图,直观展示数据分布

适用场景:
- 分析文本嵌入的质量
- 观察不同评分评论在向量空间中的分布
- 验证 Embedding 是否能有效区分不同类别的文本
"""

# ==================== 导入必要的库 ====================
import pandas as pd          # 数据处理库,用于读取和操作 CSV 文件
import numpy as np           # 数值计算库,用于矩阵运算
import ast                   # Python 抽象语法树模块,用于安全地解析字符串
import matplotlib.pyplot as plt  # 绘图库,用于创建可视化图表
import matplotlib            # Matplotlib 核心模块,用于配置颜色映射
from sklearn.manifold import TSNE  # T-SNE 降维算法实现

# ==================== 配置中文字体支持 ====================
# 设置 matplotlib 支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# ==================== 读取数据 ====================
# 从 CSV 文件中读取数据,文件应包含至少两列:
# - 'embedding': 字符串格式的 Embedding 向量,如 "[1.222, 34343, 5.4343]"
# - 'Score': 评论评分(通常是 1-5 分)
df = pd.read_csv('datas/embedding_output_1k.csv')

# 打印第一条记录的 embedding,查看原始数据格式
print(df['embedding'][0])
# 确认数据类型是字符串(str)
print(type(df['embedding'][0]))  # str = '[1.222, 34343, 5.4343]'

# ==================== 数据预处理:字符串转向量 ====================
# 使用 ast.literal_eval 安全地将字符串格式的列表转换为真正的 Python 列表
# 例如: "[1.2, 3.4, 5.6]" -> [1.2, 3.4, 5.6]
# 为什么不用 eval()? 因为 eval() 可以执行任意代码,有安全风险
# ast.literal_eval 只能解析基本的 Python 数据结构(列表、字典、数字、字符串等),更安全
df['embedding_vec'] = df['embedding'].apply(ast.literal_eval)

# 验证转换结果
print(len(df['embedding_vec'][0]))  # 打印向量的维度(长度)
print(type(df['embedding_vec'][0]))  # 确认类型已变为 list

# ==================== T-SNE 降维 ====================
# T-SNE (t-Distributed Stochastic Neighbor Embedding) 是一种非线性降维算法
# 它可以将高维数据(如 768 维的 Embedding)映射到 2D 或 3D 空间
# 优点:能很好地保持数据的局部结构,相似的点在低维空间中也会靠近
# 缺点:计算复杂度较高,不适合超大规模数据集

# 检查所有 embedding 向量的维度是否一致
# nunique() 返回不同值的个数,如果等于 1 说明所有向量长度相同
# 这是必要的,因为 T-SNE 要求输入矩阵的每一行维度必须相同
if df['embedding_vec'].apply(len).nunique() == 1:
    # 将所有向量堆叠成一个二维 NumPy 数组(矩阵)
    # 形状: (样本数量, 向量维度),例如 (1000, 768)
    matrix = np.vstack(df['embedding_vec'].values)

    # 创建 T-SNE 模型实例,配置关键参数:
    # - n_components=2: 降维到 2 维(用于 2D 可视化)
    # - perplexity=15: 困惑度,影响局部和全局结构的平衡
    #   一般取值 5-50,值越大考虑的全局结构越多
    # - random_state=42: 随机种子,保证结果可复现
    # - init='random': 初始化方式,'random' 或 'pca'
    # - learning_rate=200: 学习率,控制优化过程的步长
    tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)

    # 执行降维:将高维矩阵转换为 2D 坐标
    # 输出形状: (样本数量, 2),每行是一个点的 (x, y) 坐标
    matrix_2d = tsne.fit_transform(matrix)

    # 打印降维后的坐标(可选,用于调试)
    print(matrix_2d)

    # ==================== 可视化配置 ====================
    # 定义 5 种颜色,对应 5 个评分等级(1-5 星)
    # red(红): 1星, darkorange(深橙): 2星, gold(金): 3星,
    # turquoise(青绿): 4星, darkgreen(深绿): 5星
    colors = ["red", "darkorange", "gold", "turquoise", "darkgreen"]

    # 提取 2D 坐标的 x 和 y 轴数据
    x = matrix_2d[:, 0]  # 所有点的第一个维度(横坐标)
    y = matrix_2d[:, 1]  # 所有点的第二个维度(纵坐标)

    # 获取每个样本的评分,并转换为颜色索引
    # 评分范围是 1-5,但颜色列表索引是 0-4,所以需要减 1
    # 例如: Score=1 -> 索引0(红色), Score=5 -> 索引4(深绿色)
    colors_indices = df.Score.values - 1

    # 创建自定义颜色映射(Colormap)
    # ListedColormap 将颜色列表转换为 matplotlib 可用的颜色映射对象
    color_map = matplotlib.colors.ListedColormap(colors)

    # ==================== 绘制散点图 ====================
    # 创建散点图:
    # - x, y: 点的坐标
    # - c: 点的颜色(使用评分对应的颜色索引)
    # - cmap: 颜色映射方案
    # - alpha=0.3: 透明度(0-1),降低透明度可以避免点重叠时遮挡
    plt.scatter(x=x, y=y, c=colors_indices, cmap=color_map, alpha=0.3)

    # 设置图表标题
    plt.title('使用T-SNE降维后的亚马逊评论')

    # 显示图表
    plt.show()

else:
    # 如果向量维度不一致,无法进行 T-SNE 降维
    print("错误:Embedding 向量的维度不一致,无法进行降维!")
    print("请检查数据源,确保所有 embedding 向量长度相同。")
