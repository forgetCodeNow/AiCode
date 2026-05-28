# PDF智能翻译助手

基于大语言模型的PDF文档智能翻译系统，支持文本和表格内容的自动识别与翻译，输出格式支持PDF、Markdown等多种格式。

## 项目概述

本项目是一个自动化PDF书籍翻译工具，利用OpenAI兼容的大语言模型API（如通义千问、GLM等）实现中英文等多语言之间的智能翻译。系统采用模块化设计，支持PDF解析、内容翻译、格式化输出等完整流程。

### 核心特性

- **智能PDF解析**：自动识别并分离文本和表格内容
- **多模型支持**：兼容OpenAI API标准的多种大语言模型（通义千问、GLM等）
- **多格式输出**：支持PDF、Markdown格式的输出（Word格式预留接口）
- **表格保留**：翻译过程中保持表格结构和格式
- **重试机制**：API调用失败时自动重试3次，包含速率限制处理
- **灵活配置**：支持配置文件和命令行参数两种方式
- **详细日志**：基于loguru的结构化日志记录

## 技术栈

### 核心依赖

| 依赖包 | 版本要求 | 用途 |
|--------|---------|------|
| Python | 3.8+ | 运行时环境 |
| openai | - | OpenAI API客户端 |
| pdfplumber | - | PDF文件解析 |
| reportlab | - | PDF文件生成 |
| pandas | - | 表格数据处理 |
| PyYAML | - | YAML配置文件解析 |
| loguru | - | 日志记录 |
| pillow | - | 图像处理支持 |
| simplejson | - | JSON数据处理 |
| requests | - | HTTP请求 |

### 架构模式

- **面向对象设计**：Book-Page-Content三层数据结构
- **策略模式**：支持多种AI模型切换
- **工厂模式**：根据配置动态创建翻译器实例

## 项目结构

```
PythonProject/
├── main.py                    # 程序入口
├── config.yaml                # 配置文件
├── requestments.txt           # 依赖包列表
├── ai_model/                  # AI模型模块
│   ├── __init__.py
│   ├── model.py              # 模型基类
│   ├── openai_model.py       # OpenAI兼容模型实现
│   └── glm_model.py          # GLM模型实现
├── book/                      # 数据结构模块
│   ├── __init__.py
│   ├── book.py               # 书籍对象
│   ├── page.py               # 页面对象
│   └── content.py            # 内容对象（文本/表格）
├── translator/                # 翻译器模块
│   ├── __init__.py
│   ├── book_translation.py   # PDF翻译主逻辑
│   ├── pdf_parser.py         # PDF解析器
│   └── file_writer.py        # 文件写入器
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── log_utils.py          # 日志工具
│   ├── loader_config.py      # 配置加载器
│   ├── argumentUtils.py      # 命令行参数解析
│   └── exception.py          # 自定义异常
├── fonts/                     # 字体资源
│   └── simsun.ttc            # 宋体字体文件
├── test/                      # 测试文件
│   ├── test.pdf              # 测试PDF
│   └── The_Old_Man_of_the_Sea.pdf
├── output/                    # 输出目录
└── logs/                      # 日志目录
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境（可选）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requestments.txt
```

### 2. 配置模型

编辑 `config.yaml` 文件，配置API密钥和模型信息：

```yaml
OpenAIModel:
  model: "qwen3.6-plus"                          # 模型名称
  api_key: "your-api-key-here"                   # API密钥
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"  # API地址

GLMModel:
  model_url: ""                                  # GLM模型URL
  timeout: 300                                   # 超时时间（秒）

common:
  book: "./test/test.pdf"                        # 默认输入文件路径
  file_format: "pdf"                             # 输出格式（pdf/markdown/word）
  out_file_path: "./test/test_translated.pdf"    # 输出文件路径
```

### 3. 运行翻译

#### 方式一：使用默认配置

```bash
python main.py
```

#### 方式二：命令行参数

```bash
python main.py \
  --config config.yaml \
  --model_type OpenAiModel \
  --openai_model qwen3.6-plus \
  --openai_api_key your-api-key \
  --base_url https://dashscope.aliyuncs.com/compatible-mode/v1 \
  --book ./test/test.pdf \
  --file_format pdf
```

### 4. 查看结果

翻译完成后，输出文件将保存在指定路径（默认为原文件名加 `_translated` 后缀）。

## 使用说明

### 命令行参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--config` | str | config.yaml | 配置文件路径 |
| `--model_type` | str | OpenAiModel | 模型类型（OpenAiModel/GLMModel） |
| `--openai_model` | str | - | OpenAI模型名称 |
| `--openai_api_key` | str | - | OpenAI API密钥 |
| `--base_url` | str | dashscope地址 | API基础URL |
| `--glm_model_url` | str | - | GLM模型访问地址 |
| `--timeout` | str | - | API请求超时时间 |
| `--book` | str | config配置 | 需要翻译的PDF文件路径 |
| `--file_format` | str | pdf | 输出文件格式（pdf/markdown/word） |

### 支持的模型

1. **通义千问（推荐）**
   - 模型：qwen3.6-plus, qwen-max, qwen-turbo等
   - API地址：https://dashscope.aliyuncs.com/compatible-mode/v1
   - 优势：中文翻译质量高，国内访问速度快

2. **GLM系列**
   - 智谱AI的GLM模型
   - 需配置独立的model_url

3. **其他OpenAI兼容模型**
   - 任何符合OpenAI API标准的模型均可使用

### 输出格式

- **PDF格式**：使用reportlab生成，支持中文字体（SimSun），保留表格样式
- **Markdown格式**：纯文本输出，表格使用Markdown语法
- **Word格式**：预留接口（待实现）

## 架构设计

### 核心类图

```
┌─────────────────┐
│     Model       │ (抽象基类)
│  - request_model()
│  - make_prompt()
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────────┐
│OpenAI│  │  GLMModel  │
│Model │  │            │
└──────┘  └────────────┘

┌─────────────────┐
│   Book          │
│  - file_path    │
│  - pages[]      │
└────────┬────────┘
         │
    ┌────▼────┐
    │  Page   │
    │ -contents[]│
    └────┬────┘
         │
    ┌────▼──────────┐
    │   Content     │
    │ - TEXT        │
    │ - TABLE       │
    │ - IMAGE       │
    └───────────────┘

┌──────────────────┐
│  PDFTranslator   │
│  - model         │
│  - writer        │
│  - book_translation()│
└──────────────────┘
```

### 数据流

```
PDF文件 → pdf_parser → Book对象 → PDFTranslator
                                    ↓
                              逐页遍历内容
                                    ↓
                              调用AI模型翻译
                                    ↓
                              FileWriter写入
                                    ↓
                              输出文件(PDF/MD)
```

### 关键流程

1. **初始化阶段**
   - 解析命令行参数
   - 加载YAML配置文件
   - 创建AI模型实例
   - 创建PDF翻译器

2. **PDF解析阶段**
   - 使用pdfplumber打开PDF
   - 提取每页的文本和表格
   - 去除文本中的表格重复内容
   - 构建Book-Page-Content树形结构

3. **翻译阶段**
   - 遍历所有页面的所有内容块
   - 根据内容类型生成Prompt
   - 调用AI模型API进行翻译
   - 设置翻译结果和状态

4. **输出阶段**
   - 根据指定格式选择Writer
   - PDF：注册中文字体，创建段落和表格
   - Markdown：生成标准Markdown语法
   - 保存文件到指定路径

## 注意事项

### API密钥安全

⚠️ **重要提示**：`config.yaml` 中包含API密钥，请勿提交到公开代码仓库。建议：

1. 将 `config.yaml` 添加到 `.gitignore`
2. 使用环境变量存储敏感信息
3. 使用示例配置文件 `config.yaml.example`

### 字体依赖

PDF输出需要中文字体支持，确保 `fonts/simsun.ttc` 文件存在。如需使用其他字体，修改 `file_writer.py` 中的字体注册代码。

### 页数限制

可通过命令行参数 `--pages` 限制翻译页数，用于测试或节省API费用。

### 网络稳定性

- API调用有3次重试机制
- 遇到速率限制时会自动等待10秒
- 建议设置合理的timeout值

### 已知限制

1. 图片内容暂不支持翻译（ContentType.IMAGE已定义但未实现）
2. Word输出功能未实现
3. 复杂表格可能存在格式丢失
4. 超长文本可能需要分段处理

## 日志系统

日志文件保存在 `logs/translation.log`，包含以下级别：

- **DEBUG**：详细的调试信息（Prompt、翻译前后对比）
- **INFO**：关键操作记录（模型连接、文件写入完成）
- **WARNING**：警告信息（翻译失败、格式问题）
- **ERROR**：错误信息（API异常、文件错误）

日志格式示例：
```
20260528 22:30:15 | MainProcess | Thread-1 | module.function:42 | INFO: 模型调用成功！当前使用模型：qwen3.6-plus
```

## 常见问题

### Q1: 如何更换翻译模型？

修改 `config.yaml` 中的 `OpenAIModel.model` 字段，或通过 `--openai_model` 参数指定。

### Q2: 翻译速度慢怎么办？

- 检查网络连接
- 使用国内模型（如通义千问）
- 减少单次翻译页数
- 调整timeout参数

### Q3: PDF输出中文乱码？

确保 `fonts/simsun.ttc` 文件存在且路径正确。可在 `file_writer.py` 中更换其他中文字体。

### Q4: 如何只翻译部分页面？

目前版本暂未在命令行暴露pages参数，可修改 `main.py` 中调用 `book_translation` 时传入pages参数。

## 开发计划

- [ ] 实现图片OCR翻译功能
- [ ] 完善Word格式输出
- [ ] 添加批量翻译支持
- [ ] 实现翻译缓存机制
- [ ] 增加进度条显示
- [ ] 支持更多文件格式（EPUB、DOCX等）
- [ ] 添加Web界面

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过Issue反馈。
