from enum import Enum, auto

import pandas as pd
from utils.log_utils import log


class ContentType(Enum):
    '''""" 内容的类型 枚举"""'''
    TEXT = auto()
    TABLE = auto()
    IMAGE = auto()

class Content:

    '''书中的文本内容'''
    def __init__(self, content_type: ContentType, original, translation=None):
        '''
        内容初始化
        :param content_type:类型
        :param original:原文
        :param translation:翻译之后的
        '''
        self.content_type = content_type
        self.original = original
        self.translation = translation
        self.status = False # 翻译完成的状态


    def set_translation(self, translation, status):
        '''设置翻译后的文本和状态'''
        if self.content_type == ContentType.TEXT and isinstance(translation, str) and status:
            self.translation = translation
            self.status = status
        else:
            log.warning('输入的translation不是字符串！')

    def get_original_to_string(self):
        return self.original

class TablesContent:

    '''书中的文本内容'''
    def __init__(self, content_type: ContentType, original, translation=None):
        '''
        内容初始化
        :param content_type:类型
        :param original:原文
        :param translation:翻译之后的
        '''
        df = pd.DataFrame(original)
        self.content_type = content_type
        self.original = df
        self.translation = translation
        self.status = False # 翻译完成的状态

    def set_translation(self, translation, status):
        '''、
        设置翻译后的表格和状态
        1、判断数据合法性
        2、translation文本数据变成二维数组
        3、把二维数据变成DataFrame格式
        '''

        if self.content_type == ContentType.TABLE and isinstance(translation, str) and status:
            table_data = [row.strip().split() for row in translation.strip().split('\n')]
            # 得到DataFrame数据，表头单独处理
            translation_df = pd.DataFrame(table_data[1:], columns=table_data[0])
            log.debug('制表后的表格数据：{}'.format(translation_df))
            self.translation = translation_df
            self.status = status

    def get_original_to_string(self):
        '''
        把DataFrame格式的表格转成字符串
        :return:
        '''
        return self.original.to_string(header=False, index=False)