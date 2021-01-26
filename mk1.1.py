# -*- coding: utf-8 -*-
# @Time     : 2021/1/22
# @Author   : hjhcos
# @File     : mk1.1.py
# @Project  : mark_app
# @Software : PyCharm
# =============================

import re
import os
from typing import Optional, Union, List, Tuple


class Base(object):

    def __init__(self):
        self.RE = re.compile
        self.findall = re.findall
        self.search = re.search
        self.sub = re.sub
        pass

    def __str__(self):
        pass


class MD(Base):
    """ md标记
    1. 实现标记功能映射
    2. 实现标记匹配
        1. 实现标记与内容分割
        2. 实现标记与内容融合
    3. 实现标记转换
    4. 说明文档
    """

    def __init__(self, file=None, temp=True):
        super().__init__()
        self.tags = ('#', '>', '`', '$', '_', '*', '-', '+', '~', '\\', '[', ']', '^', '(', ')', '|')
        self.stop = False  # 是否停止样式检测的状态
        self.match = ''  # 匹配标记
        self.result = []  # 存放每段索引标记信息 [[['*', (start, end)], ['_', (start, end)]...], [['_', (start, end)]]]

        if file:
            file = os.path.abspath(file)
            with open(file, 'r', encoding='utf-8') as fd:
                self.file = self.format(fd)
            if temp:
                with open(file.split('.')[0]+'.tmp', 'w', encoding='utf-8') as f:
                    f.write(str(self.file))

    def division(self, string):
        """ 分割 ===》 内容与标记分割 只处理样式标签"""
        # print("MD.division", string)
        pass

    def detection(self, string) -> List[str, Tuple[int, int]]:
        """ 检测 --> 样式标记检测"""
        print("MD.detection", string)
        self.tags = ['*', '-', '_', '$', '`', '~']
        match_tag = ''  # 当前标记
        matching = []   # 开始标记存放 待匹配
        matched = []    # 匹配到的标记
        # start = 0      # 标记内容开头索引
        # end = 0        # 标记内容结尾索引
        # 检测标记是否有结尾符
        for index, char in enumerate(string):
            if char in self.tags:
                if not match_tag:
                    match_tag = char
                    if index+1 == len(string):
                        self.stop = True
                        self.match = match_tag
                elif char == match_tag[0]:
                    match_tag += char
                    if index+1 == len(string):
                        if match_tag in matching:
                            self.stop = True
                            self.match = match_tag
                # elif match_tag in matching:
                #     self.stop = True
                else:
                    if match_tag in matching:
                        self.stop = True
                        self.match = match_tag
                    start = index
                    matching.append(match_tag)
                    matching.append(start)
                    match_tag = char
            else:
                if match_tag:
                    if match_tag in matching:
                        self.stop = True
                        self.match = match_tag
                        match_tag = ''
                    else:
                        if match_tag:
                            start = index
                            matching.append(match_tag)
                            matching.append(start)
                            match_tag = ''

            if self.stop:
                start = matching.index(self.match)
                matching.pop(start)
                temp = start
                start = matching[start]
                end = index - len(self.match)
                matched.append([self.match, (start, end)])
                matching.pop(temp)
                self.stop = False
        if matched:
            """ 判断是否真正拥有数据"""
            # TODO: 分割数据是否正确
            self.division(matched)
            # TODO: 返回最后结果
        return match_tag

    def row_process(self, string: str) -> List[List[str, Tuple[int, int]]]:
        """
        行处理器  -->  检测、分割

        :return:
            str: 标记
            tuple: tuple(start, end)
            start: 标记内容开始索引
            end: 标记内容结尾索引
        """
        result = []
        if string == '':  # 防止没有字符串的情况
            # 脏数据舍弃
            return [['\n', (None, None)]]
        elif string[0] == '\t':
            # TODO: 处理嵌入列表的情况
            string = string[1:]
            result.append(['\t', (1, -1)])
            result.append(self.detection(string))
            # TODO: 结果返回
            return result
        self.tags = ['#', '>', '`', '$', '-', '+']
        # 处理 # >
        if string[0] in ['#', '>']:
            # 同时处理 # >
            string = string.split(' ')
            tag = string[0]
            string = ' '.join(string[1:])
            result.append([tag, (len(tag), -1)])
            result.append(self.detection(string))
            # TODO: 结果返回
            return result
        # 处理 ` $
        elif string[0] in ['`', '$']:
            # TODO: 标记判别 `、$ 是否换行
            # TODO: 内部不进行其他样式识别
            # TODO: 切换为换行标记可以获取到中间正确内容
            if string[0] == string[1]:
                pass
        # 处理其他情况
        else:
            result.append(self.detection(string))
            # TODO: 结果返回
            return result

    def process(self):
        """
        处理器 --> 行处理 保存结果
        :return: None
        """
        if not isinstance(self.file, str):
            raise TypeError(f'self.file is not str_type, it is {type(self.file)}')
        for row in self.file:
            # TODO: 对空标记列表进行识别
            # TODO: 对换行数据标记进行识别
            self.result.append(self.row_process(row))

    @staticmethod
    def format(file) -> str:
        """
        重新格式化

        :type file: io.TextIO
        :return: string
        """
        
        format_file = ''
        for string in file.readlines():
            if (not string) or (string == '\n'):
                format_file += str(string)
            elif string[0] == '\t' or string[:4] == '    ':
                format_file += str('\t'+string[1 if string[0] == "\t" else 4:])
            else:
                string = string.strip()
                if string[0] in ['#', '>']:
                    string = string.split(' ')
                    if string[0][-1] == '#':
                        if len(string) != 1:
                            format_file += str(' '.join(string)+'\n')
                    elif string[0][-1] == '>':
                        string = ' '.join(string)
                        for index, char in enumerate(string):
                            if char != '>' and char != ' ':
                                char = string[:index].replace(' ', '')
                                string = string[index:]
                                format_file += str(char+' '+string+'\n')
                                break
                    else:
                        string = ' '.join(string)
                        tag = ''
                        if string[0] == '#':
                            string = string.split('#')
                            tag = '#'
                        else:
                            string = string.split('>')
                            tag = '>'
                        for index, char in enumerate(string):
                            if char:
                                string = f'{tag}'.join(string[index:])
                                format_file += str(tag*index+' '+string+'\n')
                                break
                else:
                    format_file += str(string + '\n')
        return format_file

    def load(self, string):
        """ 加载器 -->    数据实时返回"""
        pass


if __name__ == '__main__':
    md = MD(file='blog.md')
    # for row in md.file.split('\n'):
    #     md.row_process(row)
    print(md.result)
    # for i in t:
    #     md.process(i)
