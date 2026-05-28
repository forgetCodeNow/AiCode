# 使用指南

本指南详细介绍如何配置、使用和扩展PDF智能翻译助手。

## 目录

- [环境搭建](#环境搭建)
- [配置详解](#配置详解)
- [基础使用](#基础使用)
- [高级用法](#高级用法)
- [故障排除](#故障排除)
- [最佳实践](#最佳实践)

---

## 环境搭建

### 系统要求

- **操作系统**: Windows 10/11, Linux, macOS
- **Python版本**: 3.8 或更高（推荐 3.11）
- **内存**: 至少 2GB RAM
- **磁盘空间**: 至少 500MB（包含依赖包）

### 步骤1: 安装Python

#### Windows
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.11 安装包
3. 运行安装程序，**务必勾选 "Add Python to PATH"**
4. 验证安装：
   ```bash
   python --version
   # 应输出: Python 3.11.x
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

#### macOS
```bash
brew install python@3.11
```

### 步骤2: 克隆项目

```bash
# 如果项目已存在，跳过此步骤
cd C:\Users\Administrator\Desktop\PythonCode\PythonProject
```

### 步骤3: 创建虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

激活后，命令行提示符前会显示 `(.venv)`。

### 步骤4: 安装依赖

```bash
pip install -r requestments.txt
```

**国内用户加速**（使用清华源）：
```bash
pip install -r requestments.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 步骤5: 验证安装

```bash
python -c "import openai, pdfplumber, reportlab; print('所有依赖安装成功！')"
```

---

## 配置详解

### 配置文件结构

`config.yaml` 是项目的核心配置文件，采用YAML格式。

```yaml
OpenAIModel:
  model: "qwen3.6-plus"
  api_key: "sk-33025c4ffca341b28fbcb6ed9d6ac3d4"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"

GLMModel:
  model_url: ""
  timeout: 300

common:
  book: "./test/test.pdf"
  file_format: "pdf"
  out_file_path: "./test/test_translated.pdf"
```

### 配置项说明

#### OpenAIModel 配置块

| 配置项 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| `model` | string | 是 | 模型名称 | `qwen3.6-plus`, `qwen-max`, `gpt-4` |
| `api_key` | string | 是 | API密钥 | `sk-xxx` |
| `base_url` | string | 是 | API端点URL | 见下方常用API地址 |

#### GLMModel 配置块

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `model_url` | string | 否 | GLM模型的访问地址 |
| `timeout` | integer | 否 | 请求超时时间（秒），默认300 |

#### common 配置块

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `book` | string | 是 | 输入PDF文件路径 |
| `file_format` | string | 是 | 输出格式（pdf/markdown/word） |
| `out_file_path` | string | 否 | 输出文件路径（可选） |

### 常用API地址配置

#### 通义千问（阿里云）

```yaml
OpenAIModel:
  model: "qwen3.6-plus"
  api_key: "sk-your-key-here"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

**可用模型**:
- `qwen3.6-plus`: 平衡性能和速度（推荐）
- `qwen-max`: 最高质量，适合复杂文本
- `qwen-turbo`: 快速响应，适合简单文本

**获取API密钥**:
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 开通DashScope服务
4. 创建API Key

#### 智谱GLM

```yaml
OpenAIModel:
  model: "glm-4"
  api_key: "your-glm-key"
  base_url: "https://open.bigmodel.cn/api/paas/v4"
```

#### OpenAI GPT

```yaml
OpenAIModel:
  model: "gpt-4-turbo"
  api_key: "sk-openai-key"
  base_url: "https://api.openai.com/v1"
```

### 环境变量配置（推荐）

为避免在配置文件中硬编码API密钥，可使用环境变量：

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-your-key"
$env:OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

#### Linux/Mac
```bash
export OPENAI_API_KEY="sk-your-key"
export OPENAI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
```

然后在代码中读取：
```python
import os
api_key = os.getenv('OPENAI_API_KEY')
```

### 配置文件最佳实践

1. **不要提交真实密钥到Git**
   ```bash
   # .gitignore 文件中添加
   config.yaml
   ```

2. **创建示例配置文件**
   ```yaml
   # config.yaml.example
   OpenAIModel:
     model: "your-model-name"
     api_key: "your-api-key-here"
     base_url: "your-api-url"
   ```

3. **使用不同环境的配置**
   ```
   config.dev.yaml      # 开发环境
   config.production.yaml  # 生产环境
   ```

---

## 基础使用

### 方式一：使用默认配置（最简单）

```bash
python main.py
```

这会：
- 读取 `config.yaml` 中的配置
- 翻译 `./test/test.pdf`
- 输出为 `./test/test_translated.pdf`

### 方式二：指定输入文件

```bash
python main.py --book ./books/my_book.pdf
```

### 方式三：完整参数指定

```bash
python main.py \
  --config config.yaml \
  --model_type OpenAiModel \
  --openai_model qwen3.6-plus \
  --openai_api_key sk-your-key \
  --base_url https://dashscope.aliyuncs.com/compatible-mode/v1 \
  --book ./input/book.pdf \
  --file_format pdf
```

### 方式四：输出为Markdown

```bash
python main.py --book ./test/test.pdf --file_format markdown
```

输出文件：`./test/test_translated.md`

### 查看帮助信息

```bash
python main.py --help
```

输出：
```
usage: main.py [-h] [--config CONFIG] [--model_type MODEL_TYPE]
               [--openai_model OPENAI_MODEL] [--openai_api_key OPENAI_API_KEY]
               [--base_url BASE_URL] [--book BOOK] [--file_format FILE_FORMAT]

书籍自动翻译器

options:
  -h, --help            show this help message and exit
  --config CONFIG       项目的整体配置文件
  --model_type MODEL_TYPE
                        选择大模型 (OpenAiModel/GLMModel)
  --openai_model OPENAI_MODEL
                        OpenAi中使用的模型
  --openai_api_key OPENAI_API_KEY
                        OpenAi中的api_key
  --base_url BASE_URL   API访问地址
  --book BOOK           需要翻译的书籍的文件路径
  --file_format FILE_FORMAT
                        翻译之后生成的文件格式
```

---

## 高级用法

### 批量翻译多个PDF

创建批处理脚本 `batch_translate.py`：

```python
import os
from utils.log_utils import log
from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator
from utils.loader_config import LoaderConfig

def batch_translate(input_dir, output_dir, config_path='config.yaml'):
    """批量翻译目录下的所有PDF文件"""

    # 加载配置
    loader = LoaderConfig(config_path)
    config = loader.load_config()

    # 初始化模型
    model = OpenAiModel(
        config['OpenAIModel']['model'],
        config['OpenAIModel']['api_key'],
        config['OpenAIModel']['base_url']
    )

    # 创建翻译器
    translator = PDFTranslator(model)

    # 获取所有PDF文件
    pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]

    log.info(f"找到 {len(pdf_files)} 个PDF文件")

    # 逐个翻译
    for idx, pdf_file in enumerate(pdf_files, 1):
        input_path = os.path.join(input_dir, pdf_file)
        output_filename = pdf_file.replace('.pdf', '_translated.pdf')
        output_path = os.path.join(output_dir, output_filename)

        log.info(f"[{idx}/{len(pdf_files)}] 开始翻译: {pdf_file}")

        try:
            translator.book_translation(
                pdf_file_path=input_path,
                out_file_format='pdf',
                target_language='中文',
                out_file_path=output_path
            )
            log.info(f"✓ 翻译完成: {output_filename}")
        except Exception as e:
            log.error(f"✗ 翻译失败 {pdf_file}: {e}")

if __name__ == '__main__':
    batch_translate('./books/input', './books/output')
```

使用方法：
```bash
python batch_translate.py
```

### 自定义目标语言

修改调用时的 `target_language` 参数：

```python
translator.book_translation(
    pdf_file_path="./test.pdf",
    target_language="日语"  # 可改为任何语言
)
```

支持的语言取决于AI模型的能力，常见选项：
- 中文、英文、日文、韩文、法文、德文、西班牙文等

### 限制翻译页数（测试用）

修改 `main.py` 中的调用：

```python
# 只翻译前5页
translator.book_translation(file_path, out_file_format, pages=5)
```

### 集成到自己的项目

```python
from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator

def translate_document(pdf_path, output_path, target_lang="中文"):
    """封装翻译功能"""
    model = OpenAiModel(
        model="qwen3.6-plus",
        api_key="your-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    translator = PDFTranslator(model)
    translator.book_translation(
        pdf_file_path=pdf_path,
        out_file_format="pdf",
        target_language=target_lang,
        out_file_path=output_path
    )

    return output_path

# 使用
result = translate_document("./input.pdf", "./output.pdf")
print(f"翻译完成: {result}")
```

### 监控翻译进度

由于当前版本没有进度条，可以通过日志监控：

```bash
# 实时查看日志
tail -f logs/translation.log

# Windows PowerShell
Get-Content logs/translation.log -Wait
```

---

## 故障排除

### 问题1: 依赖安装失败

**症状**:
```
ERROR: Could not find a version that satisfies the requirement xxx
```

**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requestments.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: ModuleNotFoundError

**症状**:
```
ModuleNotFoundError: No module named 'openai'
```

**原因**: 虚拟环境未激活或依赖未安装

**解决方案**:
```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 重新安装依赖
pip install -r requestments.txt
```

### 问题3: API调用失败

**症状**:
```
openai.RateLimitError: Rate limit exceeded
```

**原因**:
- API配额用尽
- 网络连接问题
- API密钥错误

**排查步骤**:
1. 检查API密钥是否正确
2. 确认账户余额充足
3. 测试网络连接：
   ```bash
   curl https://dashscope.aliyuncs.com/compatible-mode/v1
   ```
4. 查看详细错误日志：
   ```bash
   cat logs/translation.log
   ```

### 问题4: PDF解析错误

**症状**:
```
pdfplumber.utils.exceptions.PDFSyntaxError
```

**原因**: PDF文件损坏或加密

**解决方案**:
1. 用PDF阅读器打开文件，确认正常
2. 如果是加密PDF，先解密
3. 尝试重新导出PDF

### 问题5: 输出PDF中文乱码

**症状**: 输出的PDF中中文显示为方框或乱码

**原因**: 字体文件缺失或路径错误

**解决方案**:
1. 确认字体文件存在：
   ```bash
   ls fonts/simsun.ttc
   ```

2. 修改 `file_writer.py` 中的字体路径为绝对路径：
   ```python
   font_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'SimSun.ttc')
   pdfmetrics.registerFont(TTFont('SimSun', font_path))
   ```

3. 或使用系统自带字体：
   ```python
   # Windows
   pdfmetrics.registerFont(TTFont('SimSun', 'C:/Windows/Fonts/simsun.ttc'))
   ```

### 问题6: 表格翻译格式错乱

**症状**: 输出的表格列不对齐或内容错位

**原因**: AI返回的CSV格式不规范

**解决方案**:
1. 优化Prompt，在 `model.py` 中加强格式要求：
   ```python
   return f'''请翻译成{target_language}，严格遵守以下格式：
   - 每行代表表格的一行
   - 单元格之间用逗号分隔
   - 不要包含表头
   - 如果单元格内容为空，保留逗号

   原始表格：
   {content.get_original_to_string()}
   '''
   ```

2. 手动修复 `file_writer.py` 中的bug（第106行和第117行）

### 问题7: 内存不足

**症状**: 处理大文件时程序崩溃

**原因**: 一次性加载整个PDF到内存

**解决方案**:
1. 分批处理，每次翻译少量页面
2. 增加系统虚拟内存
3. 使用流式处理方式（需要修改代码）

---

## 最佳实践

### 1. API成本控制

**策略**:
- 先用小样本测试（1-2页）
- 选择合适的模型（turbo vs max）
- 设置页数上限
- 缓存翻译结果

**示例**:
```python
# 测试阶段：只翻译前2页
translator.book_translation("./book.pdf", pages=2)

# 确认效果后再全文翻译
translator.book_translation("./book.pdf")
```

### 2. 翻译质量优化

**技巧**:
- 选择针对翻译优化的模型
- 在Prompt中加入领域术语
- 分段翻译而非整篇翻译
- 人工校对关键章节

**示例 - 添加专业术语提示**:
```python
# 修改 model.py 的 make_prompt
def make_prompt(self, content, target_language, domain=None):
    prompt = f"请翻译成{target_language}"
    if domain:
        prompt += f"（这是{domain}领域的专业文档，请保持术语准确性）"
    prompt += f": {content.original}"
    return prompt
```

### 3. 错误处理增强

**建议**: 添加更完善的异常处理

```python
try:
    translator.book_translation(pdf_path, out_format)
except PageOutOfException as e:
    log.error(f"页数错误: {e}")
except openai.AuthenticationError:
    log.error("API密钥无效，请检查配置")
except FileNotFoundError:
    log.error(f"文件不存在: {pdf_path}")
except Exception as e:
    log.exception(f"未知错误: {e}")
```

### 4. 性能优化

**方法**:
- 异步并发调用API（需修改代码）
- 缓存已翻译的内容
- 跳过重复段落

**缓存示例**:
```python
import hashlib
import json

cache_file = "translation_cache.json"

def load_cache():
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(cache_file, 'w') as f:
        json.dump(cache, f)

def get_cache_key(text):
    return hashlib.md5(text.encode()).hexdigest()

# 使用前检查缓存
cache = load_cache()
cache_key = get_cache_key(content.original)
if cache_key in cache:
    content.set_translation(cache[cache_key], True)
else:
    # 调用API翻译
    translated, status = model.request_model(prompt)
    content.set_translation(translated, status)
    if status:
        cache[cache_key] = translated
        save_cache(cache)
```

### 5. 日志管理

**定期清理日志**:
```bash
# Linux/Mac
find logs/ -name "*.log" -mtime +30 -delete

# Windows PowerShell
Get-ChildItem logs\*.log | Where-Object LastWriteTime -LT (Get-Date).AddDays(-30) | Remove-Item
```

**日志级别调整**:
- 开发调试：DEBUG
- 生产运行：INFO
- 仅记录错误：ERROR

修改 `log_utils.py`:
```python
self.logger.add(sys.stdout, level='INFO')  # 改为INFO减少输出
```

### 6. 安全性建议

**保护API密钥**:
```python
# 不要这样做 ❌
api_key = "sk-real-key-here"

# 应该这样做 ✅
import os
api_key = os.getenv('OPENAI_API_KEY')

# 或者从加密配置文件读取
from cryptography.fernet import Fernet
```

**.gitignore 配置**:
```gitignore
# 敏感配置
config.yaml
.env

# 日志文件
logs/*.log

# 输出文件
output/*.pdf
output/*.md

# 虚拟环境
.venv/
```

### 7. 测试流程

**标准测试步骤**:
1. 准备测试PDF（包含文本和表格）
2. 翻译1-2页验证效果
3. 检查输出格式
4. 核对翻译质量
5. 全文翻译

**测试用例示例**:
```python
def test_simple_pdf():
    """测试简单文本PDF"""
    translator.book_translation("./test/simple.pdf", pages=1)

def test_table_pdf():
    """测试包含表格的PDF"""
    translator.book_translation("./test/with_table.pdf", pages=2)

def test_chinese_to_english():
    """测试中译英"""
    translator.book_translation("./test/chinese.pdf", target_language="English")
```

---

## 常见问题FAQ

### Q: 支持哪些PDF类型？

A: 支持大多数标准PDF，包括：
- ✓ 文本型PDF（由Word等导出）
- ✓ 包含表格的PDF
- ✗ 扫描版PDF（图片形式，需要OCR）
- ✗ 加密PDF（需要先解密）

### Q: 翻译速度如何？

A: 取决于：
- 网络速度
- API响应时间
- 文档长度

参考数据（通义千问）：
- 1页纯文本：约5-10秒
- 1页含表格：约10-20秒
- 100页文档：约15-30分钟

### Q: 可以翻译其他语言吗？

A: 可以，修改 `target_language` 参数即可。例如：
- `target_language="Japanese"` - 翻译成日文
- `target_language="German"` - 翻译成德文

### Q: 如何处理超大PDF（几百页）？

A: 建议：
1. 分割PDF为小文件
2. 分批翻译
3. 使用脚本自动化：
   ```python
   # 每50页一批
   for start_page in range(0, total_pages, 50):
       translator.book_translation(pdf, pages=start_page+50)
   ```

### Q: 翻译质量如何保证？

A: 建议：
1. 选择高质量模型（如qwen-max）
2. 重要文档人工校对
3. 建立术语表保持一致性
4. 分段翻译便于检查

### Q: 能否实现实时翻译进度显示？

A: 当前版本不支持，但可以自行添加：
```python
total_contents = sum(len(page.contents) for page in book.pages)
processed = 0

for page in book.pages:
    for content in page.contents:
        # ... 翻译逻辑 ...
        processed += 1
        print(f"\r进度: {processed}/{total_contents} ({processed/total_contents*100:.1f}%)", end='')
```

---

## 扩展开发

### 添加新的输出格式

以添加HTML输出为例：

1. 在 `file_writer.py` 中添加方法：
```python
def write_to_html(self, out_file_path: str = None):
    if not out_file_path:
        out_file_path = self.book.file_path.replace('.pdf', '_translated.html')

    with open(out_file_path, 'w', encoding='utf-8') as f:
        f.write('<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body>')

        for page in self.book.pages:
            f.write('<div class="page">')
            for content in page.contents:
                if content.content_type == ContentType.TEXT:
                    f.write(f'<p>{content.translation}</p>')
                elif content.content_type == ContentType.TABLE:
                    # 转换DataFrame为HTML表格
                    f.write(content.translation.to_html())
            f.write('</div>')

        f.write('</body></html>')
```

2. 在 `write_to_file()` 中添加分支：
```python
elif out_file_format.lower() == 'html':
    self.write_to_html(out_file_path)
```

### 添加OCR支持

需要集成OCR引擎（如Tesseract或PaddleOCR）：

```python
# 伪代码示例
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='ch')

def extract_text_from_image(image):
    result = ocr.ocr(image)
    return '\n'.join([line[1][0] for line in result[0]])
```

### 添加Web界面

可使用Flask或FastAPI：

```python
from flask import Flask, request, send_file

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate():
    pdf = request.files['pdf']
    pdf.save('temp.pdf')

    translator.book_translation('temp.pdf')

    return send_file('temp_translated.pdf')

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 总结

通过本指南，您应该能够：
- ✓ 正确搭建运行环境
- ✓ 配置API密钥和模型参数
- ✓ 执行基础的PDF翻译任务
- ✓ 处理常见的错误和问题
- ✓ 根据需求进行定制开发

如有其他问题，请查阅：
- [README.md](../README.md) - 项目概述
- [API_REFERENCE.md](API_REFERENCE.md) - 详细API文档
- 项目Issue区 - 社区讨论

祝您使用愉快！
