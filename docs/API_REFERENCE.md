# API 参考文档

本文档提供PDF智能翻译助手的详细API参考，包括所有公共类、方法和函数的说明。

## 目录

- [AI模型模块](#ai模型模块)
- [数据结构模块](#数据结构模块)
- [翻译器模块](#翻译器模块)
- [工具模块](#工具模块)

---

## AI模型模块

### Model (基类)

**文件**: `ai_model/model.py`

抽象基类，定义所有AI模型的接口规范。

#### 方法

##### `request_model(prompt: str)`

发送请求到AI模型。

**参数**:
- `prompt` (str): 发送给模型的提示文本

**返回**:
- 子类应实现具体的返回格式

**示例**:
```python
model = OpenAiModel(...)
result = model.request_model("请翻译成中文: Hello World")
```

##### `make_prompt(content, target_language: str)`

根据内容类型生成翻译提示。

**参数**:
- `content`: Content对象，包含原文内容
- `target_language` (str): 目标语言

**返回**:
- `str`: 生成的Prompt文本

**支持的Content类型**:
- `ContentType.TEXT`: 普通文本翻译
- `ContentType.TABLE`: 表格数据翻译

**示例**:
```python
prompt = model.make_prompt(content_obj, "中文")
# 返回: "请翻译成中文，（直接给我翻译后的文本，不需要有其他非翻译的文本回答）: Hello World"
```

---

### OpenAiModel

**文件**: `ai_model/openai_model.py`

OpenAI兼容API的模型实现，支持通义千问、GLM等符合OpenAI标准的模型。

#### 构造函数

```python
OpenAiModel(model: str, api_key: str, base_url: str)
```

**参数**:
- `model` (str): 模型名称，如 "qwen3.6-plus"
- `api_key` (str): API密钥
- `base_url` (str): API基础URL

**示例**:
```python
client = OpenAiModel(
    model="qwen3.6-plus",
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```

#### 方法

##### `request_model(prompt: str) -> tuple[str, bool]`

调用AI模型API进行翻译。

**参数**:
- `prompt` (str): 翻译提示文本

**返回**:
- `tuple[str, bool]`: (翻译后的文本, 是否成功)
  - 成功时返回 `(translated_text, True)`
  - 失败时返回 `("", False)`

**异常处理**:
- `openai.RateLimitError`: 速率限制时自动重试3次，每次间隔10秒
- `Exception`: 其他异常记录日志并返回失败状态

**重试机制**:
- 最大重试次数: 3次
- 重试间隔: 10秒
- 超过3次后抛出异常

**示例**:
```python
text, success = client.request_model("请翻译成中文: Hello")
if success:
    print(f"翻译结果: {text}")
else:
    print("翻译失败")
```

---

### OpenAiGlmModel

**文件**: `ai_model/glm_model.py`

GLM模型的实现（当前为占位实现）。

#### 构造函数

```python
OpenAiGlmModel(model: str, api_key: str, glm_model_url: str)
```

**参数**:
- `model` (str): 模型名称
- `api_key` (str): API密钥
- `glm_model_url` (str): GLM模型的访问URL

**注意**: 当前版本中 `request_model()` 方法未实现，需要补充完整实现。

---

## 数据结构模块

### Book

**文件**: `book/book.py`

表示一本PDF书籍的数据结构。

#### 构造函数

```python
Book(file_path: str)
```

**参数**:
- `file_path` (str): PDF文件的绝对或相对路径

#### 属性

- `file_path` (str): PDF文件路径
- `pages` (list[Page]): 页面对象列表

#### 方法

##### `add_page(page: Page)`

添加页面到书籍中。

**参数**:
- `page` (Page): 页面对象

**示例**:
```python
book = Book("./test.pdf")
page = Page()
book.add_page(page)
```

---

### Page

**文件**: `book/page.py`

表示书中的一页。

#### 构造函数

```python
Page()
```

#### 属性

- `contents` (list[Content]): 内容对象列表（文本、表格等）

#### 方法

##### `add_content(content: Content)`

添加内容块到页面中。

**参数**:
- `content` (Content): 内容对象

**示例**:
```python
page = Page()
text_content = Content(ContentType.TEXT, "Hello World")
page.add_content(text_content)
```

---

### ContentType

**文件**: `book/content.py`

内容类型的枚举定义。

#### 枚举值

- `TEXT`: 文本内容
- `TABLE`: 表格内容
- `IMAGE`: 图片内容（预留）

**示例**:
```python
from book.content import ContentType

content_type = ContentType.TEXT
```

---

### Content

**文件**: `book/content.py`

表示书中的文本内容块。

#### 构造函数

```python
Content(content_type: ContentType, original, translation=None)
```

**参数**:
- `content_type` (ContentType): 内容类型
- `original`: 原文内容（字符串）
- `translation`: 翻译后的内容（可选，默认为None）

#### 属性

- `content_type` (ContentType): 内容类型
- `original`: 原文
- `translation`: 译文
- `status` (bool): 翻译状态（True=成功，False=失败）

#### 方法

##### `set_translation(translation, status: bool)`

设置翻译结果和状态。

**参数**:
- `translation`: 翻译后的文本
- `status` (bool): 翻译是否成功

**验证**:
- 仅当 `content_type == ContentType.TEXT` 且 `translation` 是字符串且 `status=True` 时才设置

**示例**:
```python
content = Content(ContentType.TEXT, "Hello")
content.set_translation("你好", True)
print(content.translation)  # 输出: 你好
print(content.status)       # 输出: True
```

##### `get_original_to_string() -> str`

获取原文的字符串表示。

**返回**:
- `str`: 原文内容

---

### TablesContent

**文件**: `book/content.py`

表示书中的表格内容块，使用pandas DataFrame存储。

#### 构造函数

```python
TablesContent(content_type: ContentType, original, translation=None)
```

**参数**:
- `content_type` (ContentType): 内容类型（应为ContentType.TABLE）
- `original`: 原始表格数据（二维列表）
- `translation`: 翻译后的DataFrame（可选）

**内部处理**:
- 自动将 `original` 转换为 `pd.DataFrame` 格式

#### 属性

- `content_type` (ContentType): 内容类型
- `original` (pd.DataFrame): 原始表格
- `translation` (pd.DataFrame): 翻译后的表格
- `status` (bool): 翻译状态

#### 方法

##### `set_translation(translation: str, status: bool)`

设置翻译后的表格。

**参数**:
- `translation` (str): CSV格式的表格文本（行用换行符分隔，列用逗号分隔）
- `status` (bool): 翻译是否成功

**处理流程**:
1. 验证数据类型
2. 将CSV文本解析为二维数组
3. 转换为DataFrame格式（第一行作为表头）
4. 设置translation和status

**示例**:
```python
tables_content = TablesContent(
    ContentType.TABLE,
    [["Name", "Age"], ["Alice", "25"]]
)
tables_content.set_translation("姓名,年龄\n张三,30", True)
print(tables_content.translation)
# 输出:
#   姓名  年龄
# 0  张三  30
```

##### `get_original_to_string() -> str`

将DataFrame格式的表格转换为字符串。

**返回**:
- `str`: 不包含表头和索引的表格字符串

**用途**: 用于生成AI模型的Prompt

---

## 翻译器模块

### pdf_parser

**文件**: `translator/pdf_parser.py`

解析PDF文件并构建Book对象的工厂函数。

#### 函数签名

```python
def pdf_parser(pdf_file_path: str, pages: Optional[int] = None) -> Book
```

**参数**:
- `pdf_file_path` (str): PDF文件路径
- `pages` (Optional[int]): 需要解析的前N页，None表示全部页面

**返回**:
- `Book`: 解析后的书籍对象

**异常**:
- `PageOutOfException`: 当请求的页数超过实际页数时抛出

**处理流程**:
1. 使用pdfplumber打开PDF文件
2. 验证页数是否合法
3. 遍历每一页：
   - 提取文本内容 (`extract_text()`)
   - 提取表格内容 (`extract_tables()`)
   - 从文本中去除表格重复内容
   - 清理空白行和多余空格
   - 创建TextContent和TablesContent对象
   - 添加到Page对象
4. 返回Book对象

**文本清洗规则**:
- 移除空行
- 去除每行首尾空白
- 使用 `/n` 连接各行（注意：此处可能是bug，应该是 `\n`）

**示例**:
```python
from translator.pdf_parser import pdf_parser

book = pdf_parser("./test.pdf", pages=10)  # 只解析前10页
print(f"共解析 {len(book.pages)} 页")
```

---

### PDFTranslator

**文件**: `translator/book_translation.py`

PDF翻译的主控制器，协调整个翻译流程。

#### 构造函数

```python
PDFTranslator(model: Model)
```

**参数**:
- `model` (Model): AI模型实例（OpenAiModel或GLMModel）

#### 属性

- `book` (Book): 当前处理的书籍对象
- `model` (Model): AI模型实例
- `writer` (FileWriter): 文件写入器实例

#### 方法

##### `book_translation(...)`

执行完整的PDF翻译流程。

**函数签名**:
```python
def book_translation(
    pdf_file_path: str,
    out_file_format: str = 'PDF',
    target_language: str = '中文',
    out_file_path: str = None,
    pages: Optional[int] = None
)
```

**参数**:
- `pdf_file_path` (str): 输入PDF文件路径
- `out_file_format` (str): 输出格式（'PDF', 'markdown', 'word'）
- `target_language` (str): 目标语言，默认'中文'
- `out_file_path` (str): 输出文件路径，None则自动生成
- `pages` (Optional[int]): 翻译页数，None则全部翻译

**执行流程**:
1. 调用 `pdf_parser()` 解析PDF
2. 初始化FileWriter
3. 双重循环遍历所有页面和内容：
   - 生成翻译Prompt
   - 调用AI模型翻译
   - 设置翻译结果到Content对象
4. 调用 `writer.write_to_file()` 输出文件

**日志记录**:
- DEBUG级别：记录每个Prompt和翻译结果
- INFO级别：记录关键步骤

**示例**:
```python
from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator

model = OpenAiModel("qwen3.6-plus", "sk-xxx", "https://...")
translator = PDFTranslator(model)

translator.book_translation(
    pdf_file_path="./test.pdf",
    out_file_format="pdf",
    target_language="中文",
    pages=5
)
```

---

### FileWriter

**文件**: `translator/file_writer.py`

负责将翻译后的内容写入不同格式的文件。

#### 构造函数

```python
FileWriter(book: Book)
```

**参数**:
- `book` (Book): 包含翻译结果的书籍对象

#### 方法

##### `write_to_file(out_file_path: str = None, out_file_format: str = 'PDF')`

根据格式选择相应的写入方法。

**参数**:
- `out_file_path` (str): 输出文件路径
- `out_file_format` (str): 输出格式（'PDF', 'markdown', 'word'）

**支持格式**:
- `pdf`: 调用 `write_to_pdf()`
- `markdown`: 调用 `write_to_markdown()`
- `word`: 调用 `write_to_word()`（未实现）

**错误处理**:
- 不支持的格式会记录WARNING日志并返回

---

##### `write_to_pdf(out_file_path: str = None)`

将翻译结果写入PDF文件。

**参数**:
- `out_file_path` (str): 输出路径，None则自动生成（原文件名_translated.pdf）

**技术细节**:
- 使用reportlab库生成PDF
- 注册SimSun中文字体（路径：`../fonts/SimSun.ttc`）
- 字体大小：12pt，行高：14pt
- 页面大小：A4

**表格样式**:
- 表头：灰色背景，白色文字，14pt字体
- 表体：米色背景，居中对齐
- 边框：1px黑色实线
- 列宽：1.5英寸，行高：0.5英寸

**分页处理**:
- 每页内容后添加PageBreak（最后一页除外）

**示例**:
```python
writer = FileWriter(book)
writer.write_to_pdf("./output/translated.pdf")
```

---

##### `write_to_markdown(out_file_path: str = None)`

将翻译结果写入Markdown文件。

**参数**:
- `out_file_path` (str): 输出路径

**Markdown格式**:
- 文本：直接写入段落
- 表格：标准Markdown表格语法
  ```markdown
  | 列1 | 列2 | 列3 |
  | --- | --- | --- |
  | 值1 | 值2 | 值3 |
  ```
- 分页：使用 `------` 分隔符

**已知Bug**:
- 第106行存在拼写错误：`content.conytent_type` 应为 `content.content_type`
- 第117行列表推导式语法错误

---

##### `write_to_word(out_file_path: str = None)`

将翻译结果写入Word文件（待实现）。

**当前状态**: 空实现（pass）

---

## 工具模块

### Logger

**文件**: `utils/log_utils.py`

基于loguru的日志工具封装。

#### 单例对象

```python
from utils.log_utils import log
```

全局日志对象，可直接使用。

#### 日志配置

**控制台输出**:
- 级别：DEBUG
- 格式：时间 | 进程名 | 线程名 | 模块.方法:行号 | 级别 | 消息
- 颜色：时间(绿色)、模块/方法/行号(青色)、级别(彩色)、消息(根据级别着色)

**文件输出**:
- 路径：`logs/translation.log`
- 级别：INFO
- 编码：UTF-8
- 格式：与控制台相同（无颜色代码）

#### 使用方法

```python
from utils.log_utils import log

log.debug("调试信息")
log.info("普通信息")
log.warning("警告信息")
log.error("错误信息")
log.exception("异常信息（包含堆栈）")
```

**装饰器用法**:
```python
@log.catch  # 自动捕获并记录异常
def risky_function():
    1 / 0
```

---

### LoaderConfig

**文件**: `utils/loader_config.py`

YAML配置文件加载器。

#### 构造函数

```python
LoaderConfig(config_file_path: str)
```

**参数**:
- `config_file_path` (str): YAML配置文件路径

#### 方法

##### `load_config() -> dict`

加载并解析YAML配置文件。

**返回**:
- `dict`: 配置字典

**示例**:
```python
loader = LoaderConfig("./config.yaml")
config = loader.load_config()
model_name = config['OpenAIModel']['model']
```

---

### ArgumentUtils

**文件**: `utils/argumentUtils.py`

命令行参数解析工具。

#### 构造函数

```python
ArgumentUtils()
```

自动创建ArgumentParser并定义所有参数。

#### 支持的参数

详见README.md的"命令行参数详解"章节。

#### 方法

##### `parser_args() -> argparse.Namespace`

解析命令行参数。

**返回**:
- `argparse.Namespace`: 包含所有参数的命名空间对象

**使用示例**:
```python
args_util = ArgumentUtils()
args = args_util.parser_args()

print(args.model_type)      # 访问模型类型
print(args.openai_api_key)  # 访问API密钥
print(args.book)            # 访问书籍路径
```

---

### PageOutOfException

**文件**: `utils/exception.py`

自定义异常，当请求的页数超过总页数时抛出。

#### 构造函数

```python
PageOutOfException(total_pages: int, translation_pages: int)
```

**参数**:
- `total_pages` (int): 书籍总页数
- `translation_pages` (int): 请求翻译的页数

**异常消息格式**:
```
需要翻译的页数（X页）超过了书本的总页数（Y页）
```

**使用示例**:
```python
try:
    book = pdf_parser("./test.pdf", pages=100)
except PageOutOfException as e:
    print(f"错误: {e}")
    # 输出: 错误: 需要翻译的页数（100页）超过了书本的总页数（50页）
```

---

## 使用示例汇总

### 完整翻译流程

```python
from utils.log_utils import log
from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator
from utils.loader_config import LoaderConfig
from utils.argumentUtils import ArgumentUtils

# 1. 解析命令行参数
args_util = ArgumentUtils()
args = args_util.parser_args()

# 2. 加载配置
loader_config = LoaderConfig(args.config)
config = loader_config.load_config()

# 3. 初始化模型
model_name = args.openai_model or config['OpenAIModel']['model']
api_key = args.openai_api_key or config['OpenAIModel']['api_key']
base_url = args.base_url or config['OpenAIModel']['base_url']

client = OpenAiModel(model_name, api_key, base_url)
log.info(f"成功连接{model_name}大模型")

# 4. 创建翻译器
translator = PDFTranslator(client)

# 5. 执行翻译
file_path = args.book or config['common']['book']
out_format = args.file_format or config['common']['file_format']

translator.book_translation(
    pdf_file_path=file_path,
    out_file_format=out_format,
    target_language="中文"
)

log.info("翻译完成！")
```

### 自定义Prompt生成

```python
from book.content import Content, ContentType
from ai_model.openai_model import OpenAiModel

model = OpenAiModel(...)
content = Content(ContentType.TEXT, "Hello World")

prompt = model.make_prompt(content, "法语")
# 输出: "请翻译成法语，（直接给我翻译后的文本，不需要有其他非翻译的文本回答）: Hello World"
```

### 批量处理多个PDF

```python
import os
from translator.book_translation import PDFTranslator

translator = PDFTranslator(model)

pdf_files = [f for f in os.listdir("./books") if f.endswith('.pdf')]

for pdf_file in pdf_files:
    try:
        translator.book_translation(
            pdf_file_path=f"./books/{pdf_file}",
            out_file_format="pdf"
        )
        log.info(f"成功翻译: {pdf_file}")
    except Exception as e:
        log.error(f"翻译失败 {pdf_file}: {e}")
```

---

## 常见问题排查

### API调用失败

**症状**: 连续3次重试后仍然失败

**排查步骤**:
1. 检查网络连接
2. 验证API密钥是否正确
3. 确认base_url地址
4. 查看 `logs/translation.log` 中的详细错误信息

### PDF输出乱码

**原因**: 中文字体未正确加载

**解决方案**:
1. 确认 `fonts/simsun.ttc` 文件存在
2. 检查 `file_writer.py` 中的字体路径（可能需要调整为绝对路径）
3. 可替换为其他中文字体文件

### 表格翻译格式错误

**可能原因**:
1. AI返回的格式不符合CSV规范
2. Markdown写入时的代码bug

**建议**:
1. 在Prompt中明确要求返回格式
2. 修复 `file_writer.py` 第106行和第117行的bug

---

## 版本历史

- v1.0.0 (2026-05-28): 初始版本，支持PDF和Markdown输出
