"""
PDF 翻译服务 —— 基于 FastAPI 的 HTTP API。

提供 POST /translation 端点，接收 PDF 文件并返回翻译后的 PDF。
"""

import os

import uvicorn
from fastapi import FastAPI, File, Body, UploadFile
from starlette import status
from starlette.responses import JSONResponse, FileResponse

from ai_model.openai_model import OpenAiModel
from translator.book_translation import PDFTranslator
from utils.log_utils import log
from utils.project_config import ProjectConfig

# ---------- 应用实例 ----------
# FastAPI() 创建 ASGI 应用，后续通过 @app 装饰器注册路由
app = FastAPI()

# ---------- 常量 ----------
# 上传文件暂存目录（相对于启动脚本的工作目录）
TEMP_DIR = './temp/'


# ================================================================
# 路由：POST /translation
# ================================================================
@app.post(
    '/translation',
    summary='调用AI翻译器',
    description='上传 PDF 文件，指定源语言和目标语言，返回翻译后的 PDF',
)
def translation(
    # File() 声明该参数从 multipart/form-data 中提取文件字段
    # 类型注解必须用 fastapi.UploadFile（不能用 starlette.datastructures.UploadFile），
    # 否则 FastAPI 在生成 OpenAPI schema 时会因 Pydantic 类型校验失败而报错
    input_file: UploadFile = File(),

    # Body() 声明该参数从请求体的 JSON/form 字段中提取
    # FastAPI 根据 default 和 description 自动生成 OpenAPI 文档中的 schema
    source_language: str = Body(default='English', description='源语言'),
    target_language: str = Body(default='Chinese', description='目标语言'),
):
    """
    接收 PDF 文件，调用底层 AI 翻译器完成翻译，返回结果文件。

    请求格式：multipart/form-data
      - input_file: PDF 文件（必填）
      - source_language: 源语言（选填，默认 English）
      - target_language: 目标语言（选填，默认 Chinese）

    返回：
      成功 → FileResponse，浏览器触发文件下载
      失败 → JSONResponse { status: 500, content: "服务器错误，请查看日志！" }

    注意：此处未显式指定 response_model，因为返回值类型是 Union[FileResponse, JSONResponse]，
    FastAPI 对此不做自动 schema 推断，运行时直接返回响应对象即可。
    """
    try:
        # ---- 第1步：保存上传的 PDF 到本地临时目录 ----
        # input_file.size 为 0 表示空文件，跳过写入
        if input_file.size > 0:
            pdf_file_path = TEMP_DIR + input_file.filename
            # 'wb' 模式以二进制写入，适配 PDF 文件格式
            with open(pdf_file_path, 'wb') as f:
                # input_file.file 是一个类文件对象，read() 返回全部字节
                f.write(input_file.file.read())

        # ---- 第2步：初始化翻译器并执行翻译 ----
        translator = init_translator()
        output_file = translator.book_translation(
            pdf_file_path=pdf_file_path,
            source_language=source_language,
            target_language=target_language,
        )

        # ---- 第3步：返回翻译后的 PDF ----
        # FileResponse 是 Starlette 的异步文件响应：
        #   - 自动设置 Content-Type（根据扩展名推断为 application/pdf）
        #   - filename 参数控制 Content-Disposition 头，浏览器据此显示下载文件名
        return FileResponse(output_file, filename=input_file.filename)

    except Exception as e:
        # 捕获所有异常，记录完整堆栈后返回 500
        log.exception(e)
        # JSONResponse 直接返回 JSON 字符串，不经过 FastAPI 的序列化管线
        # status.HTTP_500_INTERNAL_SERVER_ERROR 即 500 状态码常量
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content='服务器错误，请查看日志！',
        )


# ================================================================
# 辅助函数：翻译器初始化
# ================================================================
def init_translator():
    """
    根据项目配置创建并返回一个 PDFTranslator 实例。

    流程：
      1. 加载项目配置（model_type、model_name、base_url 等）
      2. 根据 model_type 初始化对应的 LLM 实例
      3. 将 LLM 注入 PDFTranslator 并返回
    """
    # 加载项目级配置（从配置文件或环境变量读取）
    config = ProjectConfig()
    config.initialize()

    # 根据配置中的 model_type 创建对应的模型客户端
    # 当前仅实现 OpenAI 兼容协议（同时也兼容 DeepSeek 等国产模型）
    if config.model_type == 'OpenAIModel':
        # API Key 从环境变量 DEEPSEEK_API_KEY 读取，避免硬编码在代码中
        api_key: str = os.getenv('DEEPSEEK_API_KEY')
        model = OpenAiModel(
            config.model_name,   # 模型名称，如 deepseek-chat
            api_key,             # API 密钥
            config.base_url,     # API 端点地址，如 https://api.deepseek.com/v1
        )

    # 用模型实例创建翻译器 — 依赖注入模式，方便后续替换不同的模型实现
    translator = PDFTranslator(model)
    return translator


# ================================================================
# 入口
# ================================================================
if __name__ == '__main__':
    # uvicorn.run 启动 ASGI 服务器
    #   host='0.0.0.0' → 监听所有网络接口，允许外部访问
    #   port=8000      → 默认 HTTP 端口
    # FastAPI 的 app 本身就是 ASGI 应用，直接传给 uvicorn 即可
    uvicorn.run(app, host='0.0.0.0', port=8000)
