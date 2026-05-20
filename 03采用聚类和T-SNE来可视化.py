"""
亚马逊评论 Embedding 向量聚类与可视化脚本

功能说明:
1. 读取包含评论 Embedding 向量的 CSV 文件
2. 使用 K-Means 算法对高维向量进行聚类(分成3类)
3. 使用 T-SNE 算法将高维向量降维到 2D 空间
4. 根据聚类结果用不同颜色绘制散点图,直观展示聚类效果

适用场景:
- 无监督学习:在没有标签的情况下发现数据的自然分组
- 探索性数据分析:了解评论是否存在明显的类别划分
- 验证聚类算法的效果:通过可视化检查聚类是否合理
"""

# ==================== 导入必要的库 ====================
import pandas as pd          # 数据处理库,用于读取和操作 CSV 文件
import numpy as np           # 数值计算库,用于矩阵运算
import ast                   # Python 抽象语法树模块,用于安全地解析字符串
import matplotlib.pyplot as plt  # 绘图库,用于创建可视化图表
import matplotlib            # Matplotlib 核心模块,用于配置颜色映射
from sklearn.manifold import TSNE  # T-SNE 降维算法实现
from sklearn.cluster import KMeans # K-Means 聚类算法实现

# ==================== 配置中文字体支持 ====================
# 设置 matplotlib 支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# ==================== 读取数据 ====================
# 从 CSV 文件中读取数据,文件应包含 'embedding' 列
# embedding 是字符串格式的向量,如 "[1.222, 34343, 5.4343]"
df = pd.read_csv('datas/embedding_output_1k.csv')

# ==================== 数据预处理:字符串转向量 ====================
# 使用 ast.literal_eval 安全地将字符串格式的列表转换为真正的 Python 列表
# 例如: "[1.2, 3.4, 5.6]" -> [1.2, 3.4, 5.6]
# 为什么不用 eval()? 因为 eval() 可以执行任意代码,有安全风险
# ast.literal_eval 只能解析基本的 Python 数据结构,更安全
df['embedding_vec'] = df['embedding'].apply(ast.literal_eval)

# ==================== 检查向量维度一致性 ====================
# T-SNE 和 K-Means 都要求所有向量的维度相同
# apply(len) 计算每个向量的长度,nunique() 返回不同长度的个数
# 如果等于 1,说明所有向量长度一致,可以继续处理
if df['embedding_vec'].apply(len).nunique() == 1:

    # ==================== 构建数值矩阵 ====================
    # 将所有 embedding 向量堆叠成一个二维 NumPy 数组
    # 形状: (样本数量, 向量维度),例如 (1000, 768)
    # 每一行代表一条评论的 embedding 向量
    matrix = np.vstack(df['embedding_vec'].values)

    # ==================== K-Means 聚类 ====================
    # K-Means 是一种无监督学习算法,用于将数据分成 K 个簇(cluster)
    # 算法原理:
    # 1. 随机初始化 K 个中心点
    # 2. 将每个样本分配到最近的中心点
    # 3. 重新计算每个簇的中心点
    # 4. 重复步骤 2-3,直到中心点不再变化

    # 初始化 KMeans 对象,配置关键参数:
    # - n_clusters=3: 将数据分成 3 个簇(可以根据需求调整)
    # - init='k-means++': 智能初始化方法,比随机初始化收敛更快、效果更好
    # - random_state=43: 随机种子,保证结果可复现
    # - n_init=10: 运行 10 次不同的初始化,选择最优结果(减少陷入局部最优的风险)
    km = KMeans(n_clusters=3, init='k-means++', random_state=43, n_init=10)

    # 执行聚类:在高维空间中寻找 3 个簇
    # fit() 方法会:
    # 1. 找到 3 个最优的簇中心
    # 2. 为每个样本分配一个簇标签(0, 1, 或 2)
    km.fit(matrix)

    # 将聚类结果保存到 DataFrame 的新列 'Kmeans_Label'
    # km.labels_ 是一个数组,每个元素的值是 0、1 或 2,代表该样本属于哪个簇
    # 例如: [0, 1, 2, 0, 1, ...] 表示第1条属于簇0,第2条属于簇1,以此类推
    df['Kmeans_Label'] = km.labels_

    # ==================== T-SNE 降维 ====================
    # T-SNE (t-Distributed Stochastic Neighbor Embedding) 是一种非线性降维算法
    # 它将高维数据(如 768 维)映射到 2D 或 3D 空间,同时保持数据的局部结构
    # 相似的点在低维空间中也会靠近,便于可视化

    # 创建 T-SNE 模型实例,配置关键参数:
    # - n_components=2: 降维到 2 维(用于 2D 可视化)
    # - perplexity=15: 困惑度,影响局部和全局结构的平衡
    #   一般取值 5-50,值越大考虑的全局结构越多
    # - random_state=42: 随机种子,保证结果可复现
    # - init='random': 初始化方式,'random' 或 'pca'
    # - learning_rate=200: 学习率,控制优化过程的步长
    tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)

    # 执行降维:将高维矩阵转换为 2D 坐标
    # 输入: (1000, 768) 的高维矩阵
    # 输出: (1000, 2) 的 2D 坐标矩阵
    # 每行是一个点的 (x, y) 坐标
    matrix_2d = tsne.fit_transform(matrix)

    # 打印降维后的坐标(可选,用于调试)
    print(matrix_2d)

    # ==================== 可视化配置 ====================
    # 定义 3 种颜色,对应 3 个聚类簇
    # red(红): 簇0, green(绿): 簇1, blue(蓝): 簇2
    colors = ["red", "green", "blue"]

    # 提取 2D 坐标的 x 和 y 轴数据
    x = matrix_2d[:, 0]  # 所有点的第一个维度(横坐标)
    y = matrix_2d[:, 1]  # 所有点的第二个维度(纵坐标)

    # 获取每个样本的聚类标签(0, 1, 或 2)
    # 这些标签将直接用作颜色索引
    # 例如: label=0 -> 红色, label=1 -> 绿色, label=2 -> 蓝色
    colors_indices = df['Kmeans_Label'].values

    # 创建自定义颜色映射(Colormap)
    # ListedColormap 将颜色列表转换为 matplotlib 可用的颜色映射对象
    color_map = matplotlib.colors.ListedColormap(colors)

    # ==================== 绘制散点图 ====================
    # 创建散点图:
    # - x, y: 点的 2D 坐标(T-SNE 降维后的结果)
    # - c: 点的颜色(使用聚类标签作为颜色索引)
    # - cmap: 颜色映射方案(红/绿/蓝对应三个簇)
    # 注意:这里没有设置 alpha 透明度,所以点是不透明的
    plt.scatter(x=x, y=y, c=colors_indices, cmap=color_map)

    # 设置图表标题
    plt.title('使用聚类和T-SNE降维后的亚马逊评论')

    # 显示图表
    plt.show()

else:
    # 如果向量维度不一致,无法进行聚类和降维
    print("错误:Embedding 向量的维度不一致,无法进行处理!")
    print("请检查数据源,确保所有 embedding 向量长度相同。")
