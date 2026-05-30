import torch

# pytorch张量就是tensor，和TensorFlow是一样的，是一种多维向量
# tensor和numpy的ndarray也是一个意思

# 创建一个tensor
t1 = torch.tensor((2,4,5,))     # 返回一个列表向量tensor([2, 4, 5])
print(t1)

# 快速创建tensor的常用方法
# 创建一个0-1之间的随机数tensor
t2 = torch.rand(2, 3)

# 标准正态分布
# torch.normal()

# 全零和全1 tensor
print(torch.zeros(2, 4))
print(torch.ones(2, 4))

'''
tensor的属性
'''

#  1、shape：拿到tensor的维度
print(t2.shape)

# 2、size()方法：获取形状，也可以传shape索引
print(t2.size())
print(t2.size(-1))

# 改变形状
t2.reshape(3,2)
t2.view(3,2)

# 聚合操作
print(f'mean聚合：{t2.mean()}')


# 指定维度聚合，不写维度，默认把所有维度聚合
print(t2.sum(dim=1))
print(f'sum聚合：{t2.sum()}')