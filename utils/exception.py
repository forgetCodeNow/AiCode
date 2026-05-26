from utils.log_utils import log


class PageOutOfException(Exception):
    @log.catch
    def __init__(self, total_pages, translation_pages):
        self.total_pages = total_pages
        self.translation_pages = translation_pages
        super().__init__(f'需要翻译的页数（{self.translation_pages}页）超过了书本的总页数（{self.total_pages}页）')
