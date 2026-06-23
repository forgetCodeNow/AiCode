from reportlab.lib import pagesizes, colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, TableStyle, Table, PageBreak

from book.book import Book
from utils.log_utils import log
from book.content import ContentType


class FileWriter:
    def __init__(self, book: Book):
        self.book = book

    def write_to_file(self, out_file_path: str = None, out_file_format: str = 'PDF'):
        '''
        负责把翻译出来的数据写入一个文件
        :param out_file_path:
        :param out_file_format:
        :return:
        '''

        if out_file_format.lower() == 'pdf':
            self.write_to_pdf(out_file_path)
        elif out_file_format.lower() == 'markdown':
            self.write_to_markdown(out_file_path)
        elif out_file_format.lower() == 'word':
            self.write_to_word(out_file_path)
        else:
            log.warning('当前仅有pdf markdown word 三种输出模式')
            return

    def write_to_pdf(self, out_file_path: str = None):
        # 判断是否传入输出文件路径，没有就使用默认路径
        if not out_file_path:
            subfix = self.book.file_path[self.book.file_path.rindex('.'):]
            out_file_path = self.book.file_path.replace(subfix, '_translated.pdf')

        # 写数据到文件中
        log.debug(f'pdf原文件路径是：{self.book.file_path}, 翻译之后的输出文件路径: {out_file_path}')

        # 1、注册一个中文字体
        pdfmetrics.registerFont(TTFont('SimSun', '../fonts/SimSun.ttc'))

        # 2、创建一个pdf的文字段落样式
        style = ParagraphStyle('SimSun', fontName='SimSun', fontsize=12, leading=14)

        # 3、创建一个pdf文档
        doc = SimpleDocTemplate(out_file_path, pagesizes=pagesizes.A4)

        # 存放临时写入pdf文件的数据
        pdf_data = []

        for page in self.book.pages:  # 循环书中的所有页
            for content in page.contents:
                if content.status:
                    # 分文本和表格
                    if content.content_type == ContentType.TEXT:
                        # 写一个段落
                        paragraph = Paragraph(text=content.translation, style=style)
                        pdf_data.append(paragraph)

                    # 表格
                    if content.content_type == ContentType.TABLE:
                        # 创建表格样式
                        table_style = TableStyle(  # 表格的样式 注意(0, 0)代表一组，每组坐标为（列，行）
                            [
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'SimSun'),  # 更改表头字体为 "SimSun"
                                ('FONTSIZE', (0, 0), (-1, 0), 14),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('FONTNAME', (0, 1), (-1, -1), 'SimSun'),  # 更改表格中的字体为 "SimSun"
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)
                            ]
                        )
                        # 把DataFrame转换成列表，并且创建一个表格对象
                        table = Table(data=content.translation.values.tolist(), colWidths=1.5 * inch,
                                      rowHeights=0.5 * inch)
                        table.setStyle(table_style)  # 设置表格样式
                        pdf_data.append(table)

            # 当前这一页的内容都处理了， 紧跟着接一条分页符
            # 分页符不能加在最后一页
            if page == self.book.pages[-1]:
                pdf_data.append(PageBreak())  # 除了最后一页，其他页的后面都加上一个分页符

        doc.build(pdf_data)
        log.info('pdf写入完成')

    def write_to_markdown(self, out_file_path: str = None):
        # 判断是否传入输出文件路径，没有就使用默认路径
        if not out_file_path:
            subfix = self.book.file_path[self.book.file_path.rindex('.'):]
            out_file_path = self.book.file_path.replace(subfix, '_translated.pdf')

        with open(out_file_path, 'w', encoding='utf-8') as md:
            for page in self.book.pages:  # 循环书中的所有页
                for content in page.contents:
                    if content.status:
                        # 分文本和表格
                        if content.conytent_type == ContentType.TEXT:
                            # 写一个段落
                            md.write(content.translation)

                        # 表格
                        if content.content_type == ContentType.TABLE:
                            df = content.translation
                            header = '| ' + ' | '.join(
                                [str(column_name) for column_name in df.columns.tolist()]) + ' |' + '\n'
                            tr = '| ' + ' | '.join(['---'] * len(df.column)) + ' |' + '\n'
                            t_body = '\n'.join(['| ' + ' | '.join(
                                [str(cell) for cell in row] + ' |' for row in df.values.tolist())]) + '\n\n'
                            md.write(header + tr + t_body)

                # 当前这一页的内容都处理了， 紧跟着接一条分页符
                # 分页符不能加在最后一页
                if page == self.book.pages[-1]:
                    md.write('\n' + '------' + '\n')  # 除了最后一页，其他页的后面都加上一个分页符

        log.info('markdown写入完成')

    def write_to_word(self, out_file_path: str = None):
        pass
