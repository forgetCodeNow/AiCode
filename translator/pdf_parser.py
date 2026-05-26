from typing import Optional
from book.book import Book
from book.page import Page
from book.content import Content, ContentType, TablesContent
from utils.exception import PageOutOfException
import pdfplumber
from utils.log_utils import log


def pdf_parser(pdf_file_path: str, pages: Optional[int] = None) -> Book:
    '''
    解析PDF文件的函数，返回解析之后的文本对象
    :param pdf_file_path:pdf文件路径
    :param pages:可选的，需要翻译的前n页，默认就是整个pdf所有页
    :return: 返回一个book对象
    '''

    book = Book(pdf_file_path)  # 一个pdf对应一本书，就是一个book对象

    with pdfplumber.open(pdf_file_path) as pdf:
        # pages不能超过书本的总页数
        if pages and pages > len(pdf.pages):
            raise PageOutOfException(len(pdf.pages), pages)

        # 如果没有传pages，翻译整本书
        if not pages:
            pages_arr = pdf.pages
        else:
            pages_arr = pdf.pages[:pages]  # 通过切片截取前pages个页面


        for pdf_page in pages_arr:  # 遍历每一页
            page = Page()   # 每一页就是一个page对象

            # 从页面提取文本和表格数据
            page_text = pdf_page.extract_text()
            tables = pdf_page.extract_tables()

            # 文本内容包含表格数据内容，需要去除掉
            for table in tables:
                for row in table:
                    for cell in row:
                        page_text = page_text.replace(cell, '')

            # 处理文本数据
            if page_text:
                lines = page_text.splitlines()
                clean_lines = [line.strip() for line in lines if line.strip()]
                clean_text = '/n'.join(clean_lines)

                # 文本内容对应一个Content对象
                text_content = Content(content_type=ContentType.TEXT, original=clean_text)
                page.add_content(text_content)  # 把文件添加到page里面
                log.debug(f'[pdf解析之后的文本内容]: \n{clean_text}')

            # 处理表格数据
            if tables:
                tables_content = TablesContent(content_type=ContentType.TABLES, original=tables)
                page.add_content(tables_content)
                log.debug(f'[pdf解析之后的表格内容]: \n{tables}')

            # 把page页面添加到book里面
            book.add_page(page)



    return book
