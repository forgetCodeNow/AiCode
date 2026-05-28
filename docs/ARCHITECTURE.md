# 架构设计文档

本文档详细描述PDF智能翻译助手的系统架构、设计决策和模块交互。

## 目录

- [系统概览](#系统概览)
- [架构模式](#架构模式)
- [模块设计](#模块设计)
- [数据流设计](#数据流设计)
- [类图设计](#类图设计)
- [序列图](#序列图)
- [设计决策](#设计决策)
- [扩展性设计](#扩展性设计)

---

## 系统概览

### 系统定位

PDF智能翻译助手是一个**桌面级自动化翻译工具**，旨在：
1. 自动解析PDF文档结构（文本、表格）
2. 调用大语言模型进行智能翻译
3. 保持原文档格式输出翻译结果

### 系统边界

**输入**:
- PDF文件（支持文本和表格）
- 配置参数（模型、API密钥、输出格式等）

**输出**:
- 翻译后的文档（PDF/Markdown/Word）
- 执行日志

**非目标**:
- 不支持实时翻译
- 不支持图片OCR（预留接口）
- 不提供图形界面（CLI工具）

### 技术选型理由

| 技术 | 选择理由 |
|------|---------|
| Python 3.8+ | 丰富的PDF处理库、AI SDK支持完善 |
| pdfplumber | 优秀的PDF文本和表格提取能力 |
| reportlab | 成熟的PDF生成库，支持中文字体 |
| OpenAI兼容API | 统一接口支持多种模型（通义千问、GPT等） |
| loguru | 简洁的日志API，无需复杂配置 |
| PyYAML | 简单易用的配置文件格式 |

---

## 架构模式

### 分层架构

系统采用**三层架构**设计：

```
┌─────────────────────────────────────┐
│       表现层 (Presentation)          │
│   main.py - 命令行入口               │
│   ArgumentUtils - 参数解析           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       业务层 (Business Logic)        │
│   PDFTranslator - 翻译控制器         │
│   pdf_parser - PDF解析              │
│   FileWriter - 文件写入              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       数据层 (Data Access)           │
│   Book/Page/Content - 数据模型       │
│   OpenAiModel - AI模型客户端         │
│   LoaderConfig - 配置加载            │
└─────────────────────────────────────┘
```

**分层职责**:
- **表现层**: 处理用户输入、参数验证
- **业务层**: 核心翻译逻辑、流程控制
- **数据层**: 数据存储、外部服务调用

### 设计模式应用

#### 1. 策略模式 (Strategy Pattern)

**应用场景**: 支持多种AI模型

```python
# 抽象策略
class Model:
    def request_model(self, prompt):
        pass

# 具体策略1
class OpenAiModel(Model):
    def request_model(self, prompt):
        # OpenAI API调用逻辑

# 具体策略2
class OpenAiGlmModel(Model):
    def request_model(self, prompt):
        # GLM API调用逻辑

# 上下文使用
model = OpenAiModel(...)  # 或 OpenAiGlmModel(...)
translator = PDFTranslator(model)  # 注入策略
```

**优势**:
- 新增模型无需修改现有代码
- 运行时可切换模型

#### 2. 工厂模式 (Factory Pattern)

**应用场景**: 根据配置创建不同的翻译器

```python
# main.py 中
if args.model_type == 'OpenAiModel':
    client = OpenAiModel(model_name, api_key, base_url)
else:
    client = OpenAiGlmModel(model_name, api_key, base_url)

if out_file_format.lower() == 'pdf':
    translator = PDFTranslator(client)
```

#### 3. 组合模式 (Composite Pattern)

**应用场景**: Book-Page-Content树形结构

```
Book
├── Page 1
│   ├── Content (TEXT)
│   └── Content (TABLE)
├── Page 2
│   ├── Content (TEXT)
│   └── Content (TEXT)
└── ...
```

**优势**:
- 统一处理单个对象和组合对象
- 易于遍历和处理层次结构

#### 4. 模板方法模式 (Template Method)

**应用场景**: FileWriter的不同输出格式

```python
class FileWriter:
    def write_to_file(self, format):
        if format == 'pdf':
            self.write_to_pdf()    # 具体实现
        elif format == 'markdown':
            self.write_to_markdown()  # 具体实现

    def write_to_pdf(self):
        # PDF特有的实现细节
```

---

## 模块设计

### 模块依赖关系

```
main.py
  ├── utils.argumentUtils
  ├── utils.loader_config
  ├── ai_model.openai_model
  ├── ai_model.glm_model
  └── translator.book_translation
       ├── translator.pdf_parser
       │    ├── book.book
       │    ├── book.page
       │    └── book.content
       ├── translator.file_writer
       └── utils.log_utils
```

### 模块详细说明

#### 1. ai_model 模块

**职责**: 封装AI模型调用逻辑

**设计原则**:
- **开闭原则**: 通过继承Model基类扩展新模型
- **单一职责**: 每个模型类只负责自己的API调用

**关键设计**:
```python
class Model:
    """抽象基类，定义接口规范"""
    def request_model(self, prompt):
        raise NotImplementedError

    def make_prompt(self, content, target_language):
        """统一的Prompt生成逻辑"""
```

**重试机制**:
```python
def request_model(self, prompt):
    count = 0
    while count < 3:
        try:
            # API调用
            return result, True
        except RateLimitError:
            count += 1
            time.sleep(10)
    raise Exception("超过最大重试次数")
```

#### 2. book 模块

**职责**: 定义数据结构，表示PDF文档

**设计特点**:
- **轻量级**: 仅包含数据字段，无复杂逻辑
- **类型安全**: 使用类型提示增强代码可读性

**数据结构**:
```python
class Book:
    file_path: str
    pages: List[Page]

class Page:
    contents: List[Content]

class Content:
    content_type: ContentType  # TEXT/TABLE/IMAGE
    original: Any
    translation: Any
    status: bool
```

**设计考虑**:
- 为什么用列表而不是生成器？
  - 需要多次遍历（翻译、写入）
  - 内存占用可接受（单本书通常<100MB）

#### 3. translator 模块

**职责**: 核心翻译业务流程

**子模块**:

##### pdf_parser.py
```python
def pdf_parser(pdf_file_path, pages=None) -> Book:
    """
    纯函数式设计：输入PDF路径，输出Book对象
    无副作用，易于测试
    """
```

**解析策略**:
1. 文本和表格分别提取
2. 从文本中去除表格内容（避免重复）
3. 清理空白和空行

**已知问题**:
- 第49行：`'/n'.join(clean_lines)` 应为 `'\n'.join(clean_lines)`

##### book_translation.py
```python
class PDFTranslator:
    """
    编排整个翻译流程
    协调parser、model、writer三个组件
    """
```

**流程控制**:
```python
def book_translation(...):
    # 1. 解析
    self.book = pdf_parser(pdf_file_path)

    # 2. 翻译
    for page in self.book.pages:
        for content in page.contents:
            prompt = self.model.make_prompt(content, target_language)
            translated, status = self.model.request_model(prompt)
            content.set_translation(translated, status)

    # 3. 输出
    self.writer.write_to_file(out_file_path, out_file_format)
```

**设计改进点**:
- 当前是同步顺序处理，可改为异步并发
- 缺少进度回调机制

##### file_writer.py
```python
class FileWriter:
    """
    策略模式的体现：根据格式选择不同的写入策略
    """
```

**多态设计**:
```python
def write_to_file(self, format):
    strategies = {
        'pdf': self.write_to_pdf,
        'markdown': self.write_to_markdown,
        'word': self.write_to_word
    }
    strategy = strategies.get(format.lower())
    if strategy:
        strategy()
```

#### 4. utils 模块

**职责**: 提供通用工具函数

**模块划分**:

| 文件 | 功能 | 复用性 |
|------|------|--------|
| log_utils.py | 日志配置 | 高（任何模块可用） |
| loader_config.py | YAML加载 | 中（配置相关） |
| argumentUtils.py | 参数解析 | 中（CLI专用） |
| exception.py | 自定义异常 | 高（错误处理） |

**log_utils设计亮点**:
```python
# 单例模式：全局共享logger实例
log = Logger().get_logger()

# 使用示例
from utils.log_utils import log
log.info("消息")
```

**优点**:
- 避免重复创建logger
- 统一日志格式和输出位置

---

## 数据流设计

### 完整数据流

```
用户输入
   ↓
┌──────────────────┐
│  ArgumentUtils   │ ← config.yaml
│  解析命令行参数   │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  LoaderConfig    │
│  加载配置文件     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  OpenAiModel     │ ← model, api_key, base_url
│  创建模型实例     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  PDFTranslator   │
│  创建翻译器       │
└────────┬─────────┘
         ↓
┌──────────────────┐
│   pdf_parser     │ ← PDF文件
│  解析PDF为Book   │
└────────┬─────────┘
         ↓
      Book对象
   (pages[], contents[])
         ↓
┌──────────────────┐
│  遍历每个Content  │
│  生成Prompt      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  OpenAiModel     │
│  调用API翻译     │
└────────┬─────────┘
         ↓
   翻译结果填入Book
         ↓
┌──────────────────┐
│   FileWriter     │
│  写入目标文件     │
└────────┬─────────┘
         ↓
   输出文件(PDF/MD)
```

### 关键数据转换

#### 1. PDF → Book对象

```
原始PDF文件
   ↓ (pdfplumber.extract_text)
字符串文本
   ↓ (splitlines + strip)
清洗后的文本
   ↓ (Content对象封装)
Book.pages[].contents[]
```

#### 2. Content → Prompt

```
Content(TEXT, "Hello World")
   ↓ (make_prompt)
"请翻译成中文，（直接给我翻译后的文本...）: Hello World"
```

#### 3. API响应 → Content

```
API返回: "你好世界"
   ↓ (set_translation)
Content.translation = "你好世界"
Content.status = True
```

#### 4. Book → PDF文件

```
Book对象
   ↓ (遍历pages和contents)
reportlab Paragraph/Table对象
   ↓ (doc.build)
PDF二进制文件
```

### 状态管理

**Content对象的状态流转**:
```
创建 → translation=None, status=False
  ↓ (调用API)
翻译中 → translation=None, status=False
  ↓ (API返回成功)
已完成 → translation="译文", status=True
  ↓ (API返回失败)
已失败 → translation=None, status=False
```

**Book对象的生命周期**:
```
初始化 → book = Book(file_path)
  ↓ (解析)
填充 → book.pages添加Page对象
  ↓ (翻译)
更新 → page.contents的translation字段填充
  ↓ (写入)
消费 → FileWriter读取book生成文件
```

---

## 类图设计

### 完整类图

```
┌─────────────────────────────┐
│       <<interface>>         │
│         Model               │
├─────────────────────────────┤
│ + request_model(prompt)     │
│ + make_prompt(content, lang)│
└──────────┬──────────────────┘
           │ ▲
           │ │ implements
    ┌──────┴┴────────┐
    │                │
┌───▼──────┐  ┌─────▼────────┐
│OpenAiModel│  │OpenAiGlmModel│
├──────────┤  ├──────────────┤
│- model   │  │- model       │
│- client  │  │- client      │
├──────────┤  ├──────────────┤
│+request_ │  │+request_     │
│  model() │  │  model()     │
└──────────┘  └──────────────┘

┌─────────────────────────────┐
│        Book                 │
├─────────────────────────────┤
│- file_path: str             │
│- pages: List[Page]          │
├─────────────────────────────┤
│+ add_page(page: Page)       │
└──────────┬──────────────────┘
           │ contains 1..*
           ▼
┌─────────────────────────────┐
│         Page                │
├─────────────────────────────┤
│- contents: List[Content]    │
├─────────────────────────────┤
│+ add_content(content)       │
└──────────┬──────────────────┘
           │ contains 1..*
           ▼
┌─────────────────────────────┐
│       <<enumeration>>       │
│       ContentType           │
├─────────────────────────────┤
│ TEXT                        │
│ TABLE                       │
│ IMAGE                       │
└─────────────────────────────┘

┌─────────────────────────────┐
│        Content              │
├─────────────────────────────┤
│- content_type: ContentType  │
│- original: Any              │
│- translation: Any           │
│- status: bool               │
├─────────────────────────────┤
│+ set_translation(text, ok)  │
│+ get_original_to_string()   │
└─────────────────────────────┘

┌─────────────────────────────┐
│      TablesContent          │
├─────────────────────────────┤
│- original: DataFrame        │
│- translation: DataFrame     │
├─────────────────────────────┤
│+ set_translation(csv, ok)   │
│+ get_original_to_string()   │
└─────────────────────────────┘

┌─────────────────────────────┐
│      PDFTranslator          │
├─────────────────────────────┤
│- book: Book                 │
│- model: Model               │
│- writer: FileWriter         │
├─────────────────────────────┤
│+ book_translation(...)      │
└──────────┬──────────────────┘
           │ uses
           ▼
┌─────────────────────────────┐
│       FileWriter            │
├─────────────────────────────┤
│- book: Book                 │
├─────────────────────────────┤
│+ write_to_file(path, fmt)   │
│+ write_to_pdf(path)         │
│+ write_to_markdown(path)    │
│+ write_to_word(path)        │
└─────────────────────────────┘

┌─────────────────────────────┐
│       ArgumentUtils         │
├─────────────────────────────┤
│- parser: ArgumentParser     │
├─────────────────────────────┤
│+ parser_args()              │
└─────────────────────────────┘

┌─────────────────────────────┐
│       LoaderConfig          │
├─────────────────────────────┤
│- config_file_path: str      │
├─────────────────────────────┤
│+ load_config() -> dict      │
└─────────────────────────────┘
```

### 包图

```
┌────────────────────────────────────────┐
│           PythonProject                │
├──────────┬──────────┬────────┬─────────┤
│ ai_model │  book    │transla-│ utils   │
│          │          │  tor   │         │
├──────────┤          │        ├─────────┤
│model.py  │book.py   │book_   │log_     │
│openai_   │page.py   │transla-│ utils.py│
│ model.py │content.py │ tion.py│loader_  │
│glm_model.py         │pdf_    │ config.py│
│          │          │ parser.py│argumen-│
│          │          │file_   │ tUtils.py│
│          │          │ writer.py│except- │
│          │          │        │ ion.py  │
└──────────┴──────────┴────────┴─────────┘
```

---

## 序列图

### 主流程序列图

```
用户         main.py      ArgumentUtils  LoaderConfig  OpenAiModel  PDFTranslator  pdf_parser  FileWriter
 │             │              │              │              │              │            │            │
 │──启动──────▶│              │              │              │              │            │            │
 │             │──解析参数──▶│              │              │              │            │            │
 │             │◀──args──────│              │              │              │            │            │
 │             │──加载配置─────────────────▶│              │              │            │            │
 │             │◀──config──────────────────│              │              │            │            │
 │             │──创建模型──────────────────────────────▶│              │            │            │
 │             │◀──client────────────────────────────────│              │            │            │
 │             │──创建翻译器──────────────────────────────────────────▶│            │            │
 │             │──开始翻译──────────────────────────────────────────▶│            │            │
 │             │                                                      │──解析PDF──▶│            │
 │             │                                                      │◀──Book─────│            │
 │             │                                                      │            │            │
 │             │                    [循环: 每个Content]                │            │            │
 │             │                                                      │            │            │
 │             │──────────────────────────────────────────────────▶│            │            │
 │             │                              │──生成Prompt───▶│              │            │
 │             │                              │◀──Prompt──────│              │            │
 │             │                              │──请求翻译───▶│              │            │
 │             │                              │◀──译文────────│              │            │
 │             │                                                      │            │            │
 │             │                                                      │──写入文件──────────────▶│
 │             │                                                      │◀──完成─────────────────│
 │◀──翻译完成──│              │              │              │              │            │            │
```

### PDF解析详细流程

```
pdf_parser      pdfplumber      Book        Page       Content
    │              │             │           │           │
    │──打开PDF────▶│             │           │           │
    │◀──PDF对象────│             │           │           │
    │              │             │           │           │
    │──[循环:每页]▶│             │           │           │
    │              │──提取文本──▶│           │           │
    │              │──提取表格──▶│           │           │
    │              │◀──text─────│           │           │
    │              │◀──tables───│           │           │
    │              │             │           │           │
    │              │             │──创建Page───────────▶│
    │              │             │           │           │
    │              │             │           │──创建TextContent──▶│
    │              │             │           │◀──Content─────────│
    │              │             │           │──add_content─────▶│
    │              │             │           │           │
    │              │             │◀──Page────│           │
    │              │             │──add_page─▶│           │
    │              │             │           │           │
    │◀──Book───────│             │           │           │
```

### API调用重试机制

```
OpenAiModel     OpenAI API      time模块
    │              │              │
    │──请求API────▶│              │
    │              │              │
    │──[异常:RateLimit]           │
    │              │              │
    │──sleep(10)────────────────▶│
    │◀─────────────│              │
    │              │              │
    │──重试请求───▶│              │
    │              │              │
    │──[再次异常]──│              │
    │──sleep(10)────────────────▶│
    │              │              │
    │──第三次请求─▶│              │
    │              │              │
    │──[仍失败]────│              │
    │──抛出异常───▶│              │
```

---

## 设计决策

### 决策1: 为什么选择pdfplumber而非PyPDF2？

**对比分析**:

| 特性 | pdfplumber | PyPDF2 |
|------|-----------|--------|
| 文本提取 | ✓ 优秀 | △ 一般 |
| 表格提取 | ✓ 原生支持 | ✗ 需额外库 |
| 布局分析 | ✓ 支持 | ✗ 不支持 |
| 性能 | △ 较慢 | ✓ 较快 |
| 维护状态 | ✓ 活跃 | ✓ 活跃 |

**决策理由**:
- 项目需要处理表格，pdfplumber原生支持
- 翻译场景对性能要求不高（瓶颈在API调用）
- pdfplumber能更好地保留文本布局信息

### 决策2: 为什么用reportlab而非fpdf？

**对比**:
- **reportlab**: 功能强大，支持复杂布局和中文字体，学习曲线陡峭
- **fpdf**: 简单易用，但中文支持需要额外配置

**决策理由**:
- 需要精确控制表格样式
- reportlab的Table对象更适合结构化数据
- 团队已有reportlab使用经验

### 决策3: 为什么Book-Page-Content用组合而非继承？

**考虑因素**:
- PDF文档天然具有层次结构
- 不同类型的内容（文本、表格、图片）需要统一管理
- 未来可能扩展更多Content子类型

**决策理由**:
- 组合模式更符合"整体-部分"的关系
- 便于遍历和处理（双重for循环）
- 符合Liskov替换原则

### 决策4: 为什么同步调用而非异步？

**权衡**:
- **异步优势**: 并发调用API，提高吞吐量
- **同步优势**: 代码简单，易于理解和调试

**决策理由**:
- 初版追求快速上线
- API有速率限制，并发收益有限
- 后续可扩展为asyncio版本

**改进建议**:
```python
# 未来的异步版本
import asyncio
import aiohttp

async def translate_content(content, model):
    prompt = model.make_prompt(content, "中文")
    result = await model.async_request(prompt)
    content.set_translation(result.text, result.success)

async def translate_book(book, model):
    tasks = []
    for page in book.pages:
        for content in page.contents:
            tasks.append(translate_content(content, model))
    await asyncio.gather(*tasks)
```

### 决策5: 为什么用YAML而非JSON/TOML？

**对比**:
- **YAML**: 人类友好，支持注释，适合配置
- **JSON**: 机器友好，但不支持注释
- **TOML**: 简洁，但嵌套结构表达不如YAML清晰

**决策理由**:
- 配置文件需要人工编辑和阅读
- 需要注释说明各字段含义
- YAML在Python生态中广泛使用（PyYAML库成熟）

### 决策6: 日志为何选择loguru而非logging？

**对比**:
```python
# logging (标准库)
import logging
logger = logging.getLogger(__name__)
handler = logging.FileHandler('app.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# loguru
from loguru import logger
logger.add('app.log', level='DEBUG')
```

**决策理由**:
- loguru零配置即可用
- 自动添加颜色、时间戳、模块信息
- API更简洁（`logger.info()` vs `logger.info()`）
- 内置异常捕获装饰器 `@logger.catch`

---

## 扩展性设计

### 扩展点1: 新增AI模型

**步骤**:
1. 创建新类继承Model基类
2. 实现request_model方法
3. 在main.py中添加分支

**示例 - 添加Azure OpenAI**:
```python
# ai_model/azure_model.py
from openai import AzureOpenAI
from ai_model.model import Model

class AzureOpenAiModel(Model):
    def __init__(self, endpoint, api_key, deployment, api_version):
        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment = deployment

    def request_model(self, prompt):
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response.choices[0].message.content, True
```

**配置**:
```yaml
AzureModel:
  endpoint: "https://xxx.openai.azure.com/"
  api_key: "xxx"
  deployment: "gpt-4"
  api_version: "2024-02-15-preview"
```

### 扩展点2: 新增输出格式

**步骤**:
1. 在FileWriter中添加write_to_xxx方法
2. 在write_to_file中添加分支

**示例 - 添加HTML输出**:
```python
def write_to_html(self, out_file_path=None):
    if not out_file_path:
        out_file_path = self.book.file_path.replace('.pdf', '.html')

    with open(out_file_path, 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>翻译结果</title></head>
<body>
''')
        for page_idx, page in enumerate(self.book.pages):
            f.write(f'<div class="page" id="page-{page_idx}">\n')
            for content in page.contents:
                if content.content_type == ContentType.TEXT:
                    f.write(f'<p>{content.translation}</p>\n')
                elif content.content_type == ContentType.TABLE:
                    f.write(content.translation.to_html(index=False))
            f.write('</div>\n')
        f.write('</body></html>')
```

### 扩展点3: 新增内容类型

**当前**: TEXT, TABLE, IMAGE(未实现)

**扩展**: 公式、代码块、引用等

**步骤**:
1. 在ContentType枚举中添加
2. 在pdf_parser中添加解析逻辑
3. 在FileWriter中添加渲染逻辑

**示例 - 添加公式支持**:
```python
class ContentType(Enum):
    TEXT = auto()
    TABLE = auto()
    IMAGE = auto()
    FORMULA = auto()  # 新增

# pdf_parser中检测公式
if is_formula(element):
    formula_content = Content(ContentType.FORMULA, latex_code)
    page.add_content(formula_content)

# FileWriter中渲染
if content.content_type == ContentType.FORMULA:
    # PDF: 使用matplotlib渲染LaTeX
    # HTML: 使用MathJax
    f.write(f'\\[{content.translation}\\]')
```

### 扩展点4: 插件化架构（未来方向）

**目标**: 允许第三方开发插件

**设计思路**:
```python
# plugins/base.py
class TranslatorPlugin:
    def parse(self, file_path):
        raise NotImplementedError

    def translate(self, text):
        raise NotImplementedError

    def export(self, book):
        raise NotImplementedError

# 插件管理器
class PluginManager:
    def __init__(self):
        self.plugins = {}

    def register(self, name, plugin_class):
        self.plugins[name] = plugin_class

    def get_plugin(self, name):
        return self.plugins[name]()

# 使用
pm = PluginManager()
pm.register('pdf', PdfPlugin)
plugin = pm.get_plugin('pdf')
```

### 扩展点5: Web服务化

**改造方案**:
```python
# app.py (FastAPI)
from fastapi import FastAPI, UploadFile
from translator.book_translation import PDFTranslator

app = FastAPI()

@app.post("/translate")
async def translate(file: UploadFile, target_lang: str = "中文"):
    # 保存上传文件
    pdf_path = f"/tmp/{file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # 执行翻译
    translator = PDFTranslator(model)
    translator.book_translation(pdf_path, target_language=target_lang)

    # 返回结果
    output_path = pdf_path.replace('.pdf', '_translated.pdf')
    return FileResponse(output_path)
```

**部署**:
```bash
pip install fastapi uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## 性能优化建议

### 当前性能瓶颈

1. **API调用延迟**: 每次调用耗时1-5秒
2. **同步处理**: 串行翻译所有内容块
3. **内存占用**: 整本书加载到内存

### 优化方案

#### 1. 批量翻译

```python
# 当前：逐个翻译
for content in page.contents:
    translate(content)

# 优化：批量发送
batch = page.contents[:10]  # 每批10个
prompts = [make_prompt(c) for c in batch]
results = batch_translate(prompts)  # 一次API调用
```

#### 2. 缓存机制

```python
import hashlib

cache = {}

def cached_translate(text):
    key = hashlib.md5(text.encode()).hexdigest()
    if key in cache:
        return cache[key]
    result = model.request_model(text)
    cache[key] = result
    return result
```

#### 3. 异步并发

```python
import asyncio

async def translate_all(contents):
    tasks = [translate_async(c) for c in contents]
    return await asyncio.gather(*tasks, semaphore=5)  # 最多5并发
```

#### 4. 流式处理

```python
# 当前：全部加载到内存
book = pdf_parser(pdf_path)  # 占用大量内存

# 优化：逐页处理
for page in pdfplumber.open(pdf_path).pages:
    process_page(page)  # 处理完即释放
    write_page(page)
```

---

## 安全性考虑

### 1. API密钥保护

**风险**: config.yaml中包含明文密钥

**缓解措施**:
- 添加到.gitignore
- 使用环境变量
- 加密存储（如HashiCorp Vault）

### 2. 输入验证

**风险**: 恶意PDF文件导致崩溃

**缓解措施**:
```python
# 文件大小限制
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
if os.path.getsize(pdf_path) > MAX_FILE_SIZE:
    raise ValueError("文件过大")

# 页数限制
if len(pdf.pages) > 1000:
    raise ValueError("页数过多")
```

### 3. 输出 sanitization

**风险**: 翻译结果包含恶意脚本（HTML输出时）

**缓解措施**:
```python
import html

safe_text = html.escape(content.translation)
f.write(f'<p>{safe_text}</p>')
```

---

## 总结

本架构设计文档展示了：
- ✓ 清晰的分层架构
- ✓ 合理的设计模式应用
- ✓ 可扩展的模块设计
- ✓ 明确的数据流向
- ✓ 周全的扩展点预留

**核心设计哲学**:
1. **简单优先**: 不过度设计，满足当前需求
2. **开放封闭**: 对扩展开放，对修改封闭
3. **单一职责**: 每个模块专注一件事
4. **渐进演进**: 先实现核心功能，再逐步优化

**未来演进方向**:
- 异步化处理提升性能
- 插件化架构增强扩展性
- Web服务化扩大应用场景
- AI模型多样化提升翻译质量
