
import pandas as pd          # 数据处理库,用于读取和操作 CSV 文件
import numpy as np           # 数值计算库,用于矩阵运算
import ast                   # Python 抽象语法树模块,用于安全地解析字符串
import matplotlib.pyplot as plt  # 绘图库,用于创建可视化图表
import matplotlib            # Matplotlib 核心模块,用于配置颜色映射
from sklearn.manifold import TSNE  # T-SNE 降维算法实现

# 设置 matplotlib 支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体字体显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

df = pd.read_csv('datas/embedding_output_1k.csv')

# 把embedding列转成列表
df['embedding_vec'] = df.embeddding.apply(ast.literal_eval)

# 确保矩阵的维度都时一样的
if df['embedding_vec'].apply(len).nunique == 1:

    pass
