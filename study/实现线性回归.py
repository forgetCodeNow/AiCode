import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('../dataset/Income1.csv')

plt.scatter(data.Education, data.Income)
plt.xlabel('Education')
plt.ylabel('Income')


# 编写线性方程 wx + b
# 分解写法
w = torch.randn(1, requires_grad=True)
b = torch.zeros(1, requires_grad=True)

# 学习率
learning_rate = 0.01

X = torch.from_numpy(data.Education.values.reshape(-1, 1)).type(torch.FloatTensor)
Y = torch.from_numpy(data.Income.values).type(torch.FloatTensor)

for epoch in range(5000):
    for x, y in zip(X, Y):
        y_pred = torch.matmul(w, x) + b
        # 损失函数
        loss = (y - y_pred).pow(2).sum()

        # 梯度清零
        if w.grad is not None:
            w.grad.zero_()
        if b.grad is not None:
            b.grad.zero_()

        loss.backward(retain_graph=True)

        with torch.no_grad():
            w.data -= learning_rate * w.grad.data
            b.data -= learning_rate * b.grad.data

print(w)
print(b)

plt.scatter(data.Education, data.Income)
plt.xlabel('Education')
plt.ylabel('Income')
plt.plot(X.numpy(), (torch.matmul(X, w) + b).data.numpy(), color='red')
plt.show()


