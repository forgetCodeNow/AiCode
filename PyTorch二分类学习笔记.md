# PyTorch 实现二分类 - 学习笔记

## 📚 核心概念

### 1. 数据准备

```python
import torch
import numpy as np
import pandas as pd

# 读取数据
data = pd.read_csv('./dataset/credit-a.csv', header=None)

# 特征和标签分离（前15列为特征，最后一列为标签）
X = data.iloc[:, :-1]  # 特征矩阵 (653, 15)
Y = data.iloc[:, -1]   # 标签向量 (653,)

# 将标签从 -1/1 转换为 0/1（适配 BCELoss）
Y.replace(-1, 0, inplace=True)

# 转换为 PyTorch Tensor
X = torch.from_numpy(X.values).type(torch.FloatTensor)
Y = torch.from_numpy(Y.values.reshape(-1, 1)).type(torch.FloatTensor)
```

**关键点：**
- 输入维度：15个特征
- 输出维度：1（概率值）
- 标签范围：必须为 [0, 1] 才能使用 BCELoss

---

### 2. 模型构建

```python
from torch import nn

model = nn.Sequential(
    nn.Linear(15, 1),      # 线性层：15维 → 1维
    nn.Sigmoid()           # Sigmoid激活：输出压缩到(0,1)
)
```

**结构说明：**
- `nn.Linear(15, 1)`：全连接层，计算公式 `y = Wx + b`
- `nn.Sigmoid()`：激活函数，将输出映射为概率值
- 适用于二分类任务

---

### 3. 损失函数与优化器

```python
# 二元交叉熵损失（Binary Cross Entropy Loss）
loss_fn = nn.BCELoss()

# 随机梯度下降优化器
opt = torch.optim.SGD(model.parameters(), lr=0.001)
```

**选择原因：**
- **BCELoss**：专门用于二分类，配合 Sigmoid 输出
- **SGD**：基础优化器，学习率 0.001

---

### 4. 训练过程

```python
batch_size = 32
steps = 653 // 32  # 每轮迭代次数

for epoch in range(1000):
    for batch in range(steps):
        # 分批取数据
        start = batch * batch_size
        end = start + batch_size
        x = X[start:end]
        y = Y[start:end]

        # 前向传播
        y_pred = model(x)
        loss = loss_fn(y_pred, y)

        # 反向传播
        opt.zero_grad()     # 清空梯度
        loss.backward()     # 计算梯度
        opt.step()          # 更新参数
```

**训练流程：**
1. **前向传播**：输入 → 模型 → 预测值 → 计算损失
2. **反向传播**：清空梯度 → 计算梯度 → 更新参数
3. **批次训练**：每批32个样本，共约20批/轮，训练1000轮

---

### 5. 模型评估

```python
# 查看模型参数
print(model.state_dict())

# 计算准确率
accuracy = ((model(X).data.numpy() > 0.5) == Y.numpy()).mean()
print(f"准确率: {accuracy}")
```

**评估方法：**
- 预测概率 > 0.5 判定为正类（1）
- 预测概率 ≤ 0.5 判定为负类（0）
- 准确率 = 正确预测数 / 总样本数

---

## 🔑 关键知识点总结

| 组件 | 选择 | 原因 |
|------|------|------|
| 激活函数 | Sigmoid | 输出概率值 (0,1) |
| 损失函数 | BCELoss | 配合Sigmoid，专用于二分类 |
| 优化器 | SGD | 简单有效的基础优化器 |
| 学习率 | 0.001 | 较小学习率保证稳定收敛 |
| 批次大小 | 32 | 平衡内存和训练效率 |

---

## ⚠️ 注意事项

1. **标签转换**：原始标签为 -1/1，需转换为 0/1 才能使用 BCELoss
2. **数据reshape**：标签需要 reshape 为 `(n, 1)` 以匹配模型输出形状
3. **类型转换**：数据必须转为 `FloatTensor` 类型
4. **梯度清零**：每次反向传播前必须调用 `zero_grad()`

---

##  应用场景

- 信用评分（是否违约）
- 垃圾邮件检测
- 疾病诊断
- 欺诈检测

---

*基于 credit-a 数据集（653条样本，15个特征）*
