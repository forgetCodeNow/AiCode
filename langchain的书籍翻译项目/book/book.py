from book.page import Page


class Book:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pages: [Page] = []

    def add_page(self, page):
        self.pages.append(page)
