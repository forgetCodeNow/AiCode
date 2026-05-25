import pdfplumber
from pdfminer import layout

pdf = pdfplumber.open('./test.pdf')


# 获取每pdf注册信息
print(pdf.metadata)
# 获取PDF页数
print(pdf.pages)

page1 = pdf.pages[0]
page2 = pdf.pages[1]

# 获取单页文本数据,layout=True保留原文本格式
print(page1.extract_text(layout=True))

# 获取单页数据内的图片
print(page2.images)

# 获取单页表格数据
print(page1.extract_tables())

# 裁剪并保存图片
img = page2.images[0] # 第一张图片，一页有可能有多张图片
ppoint = (img['x0'], img['top'], img['x1'], img['bottom'])  # 定位图片在页面里面的坐标
page2.crop(ppoint).to_image(antialias=True, resolution=1080).save('./page2_01.png')

# 把整个页面变成图片,age1.bbox获取整个页面的坐标
# page1.crop(page1.bbox).to_image(antialias=True, resolution=1080).save('./page1_01.png')
