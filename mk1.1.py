# -*- coding: utf-8 -*-
# @Time     : 2021/1/22
# @Author   : hjhcos
# @File     : mk1.1.py
# @Project  : mark_app
# @Software : PyCharm
# =============================
import os
from typing import List, Tuple


class Base(object):

    def __init__(self):
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

    def __init__(self, file=None, temp=False):
        super().__init__()
        # self.tags = ['#', '>', '`', '$', '_', '*', '-', '+', '~', '\\', '[', ']', '^', '(', ')', '|']
        self.tags = ''
        # 新增属性 mode
        self.mode = 'normal'  # 造成停止的原因 table list code math
        self.stop = False  # 是否停止样式检测的状态
        self.match = ''  # 匹配标记
        self.result = []  # 存放每段索引标记信息

        if file:
            file = os.path.abspath(file)
            with open(file, 'r', encoding='utf-8') as fd:
                self.file = self.format(fd)
            if temp:
                with open(file.split('.')[0] + '.tmp', 'w', encoding='utf-8') as f:
                    f.write(str(self.file))

    def division(self, match: list):
        """ 分割 --> 内容与标记分割 只处理样式标签"""
        pass

    @staticmethod
    def detection(string: str):
        """
        检测  -->  样式标记检测

        :param string:
        :return: List[dict{}]]
        """

        # print("MD.detection", string)
        tags = ['*', '-', '_', '$', '`', '~']
        match_tag = ''  # 当前标记
        matching = []  # 开始标记存放 待匹配
        matched = []  # 匹配到的标记
        stop = False    # 标记存放引起的停止位
        match = ''  # 存放前一个匹配标记
        # start = 0      # 标记内容开头索引
        # end = 0        # 标记内容结尾索引
        # 检测标记是否有结尾符
        for tag in tags:
            if tag in string:
                break
            if tag == '~':
                return []
        for index, char in enumerate(string):
            if char in tags:
                if not match_tag:
                    match_tag = char
                    if index + 1 == len(string):
                        stop = True
                        match = match_tag
                elif char == match_tag[0]:
                    match_tag += char
                    if index + 1 == len(string):
                        if match_tag in matching:
                            stop = True
                            match = match_tag
                # elif match_tag in matching:
                #     self.stop = True
                else:
                    if match_tag in matching:
                        stop = True
                        match = match_tag
                    start = index
                    matching.append(match_tag)
                    matching.append(start)
                    match_tag = char
            else:
                if match_tag:
                    if match_tag in matching:
                        stop = True
                        match, match_tag = match_tag, ''
                    else:
                        if match_tag:
                            start = index
                            matching.append(match_tag)
                            matching.append(start)
                            match_tag = ''

            if stop:
                start = matching.index(match)
                matching.pop(start)
                temp = start
                start = matching[start]
                end = index - len(match)
                data = {
                    'tag': match,
                    'start': start,
                    'end': end
                }
                matched.append(data)
                matching.pop(temp)
                stop = False
        # 处理超链接 [][] []() [^]
        if bool('[' in string) and bool(']' in string):
            count = True
            s = string
            while count:
                start = s.find('[')
                end = s.find(']')
                try:
                    if s[start + 1] == '^':
                        pass
                    elif s[end + 1] == '(':
                        lstart = s.find('(')
                        rend = s.find(')')
                        matched.append(['[]()', (start, end, lstart, rend)])
                        end = rend
                    elif s[end + 1] == '[':
                        pass
                    else:
                        count = False
                except IndexError:
                    pass
                s = s[end + 1:]
                count = False if s.find('[') == -1 else True

        matched.sort(key=lambda x: x['start'])
        return matched

    def row_process(self, string: str):
        """
        行处理器  -->  检测、分割
        1. 换行标记触发停止位
        2. 模式之间的切换

        """

        result = []  # 存放标记
        res = ''
        if string[0] == ' ':
            # string = string[1:]
            res = {
                'tag': '\t',
                'start': 1,
                'end': -1
            }
        # 处理 # >
        elif string[0] in ['#', '>']:
            string = string.split(' ')
            tag = string[0]
            # string = ' '.join(string[1:])
            string = ' '.join(string)
            res = {
                'tag': tag,
                'start': 1,
                'end': -1,
            }
            # if self.detection(string):
            #     result.append(self.detection(string))
        elif string[0] in ['`', '$']:
            if string[:3] == '```':
                if not string.rfind('```'):
                    tag = string
                    self.tags = '```'
                    self.stop = True
                    self.mode = 'code'
                    res = {
                        'tag': tag,
                        'start': 1,
                        'end': None,
                    }
            elif string[:2] == '$$':
                if not string.rfind('$$'):
                    self.tags = '$$'
                    self.stop = True
                    self.mode = 'math'
                    res = {
                        'tag': self.tags,
                        'start': 1,
                        'end': None
                    }
        # |
        elif bool(string[0] == '|') and bool(string[-1] == '|'):
            self.mode = 'table'
            self.stop = True
            res = {
                'tag': '|',
                'start': string.count('|')-1,
                'end': None,
            }
        # + - 1.
        elif string[:2] in ['+ ', '- ', '1.']:
            tag = string.split(' ')[0]
            res = {
                'tag': tag,
                'start': 1,
                'end': None
            }
            self.stop = True
            self.mode = 'list'
        if res:
            result.append(res)
            result += self.detection(string)
        else:
            result += self.detection(string)
        # print(result)
        return result

    def process(self, file):
        """
        处理器 --> 行处理 保存结果
 
        :return: None
        """
        for row in file.split('\n'):
            # TODO: 不破坏格式化的内容
            if not row:
                self.stop = False
                self.mode = 'normal'
                self.result.append([{
                    'tag': '\n',
                    'start': None,
                    'end': None
                }])
            elif self.mode == 'normal':
                self.result.append(self.row_process(row))
            elif self.mode == 'code' or self.mode == 'math':
                if row.strip() in ['```', '$$']:
                    self.mode = 'normal'
                    self.stop = False
                    self.result.append([{
                        'tag': self.tags,
                        'start': None,
                        'end': -1
                    }])
                else:
                    self.result.append(None)
            elif self.mode == 'table':
                if (row[0] == '|') and (row[-1] == '|'):
                    self.result.append(None)
                else:
                    self.stop = False
                    self.mode = 'normal'
                    self.result.append(self.row_process(row))
            elif self.mode == 'list':
                if row.strip()[0] in ['+', '-']:
                    index = row.find('+') if row.strip()[0] == '+' else row.find('-')
                    row = row[:index].replace('    ', '\t')+''+row[index:]
                    # TODO: 返回结果
                    self.result.append(None)
                elif row.find('.') != -1:
                    if row[:row.find('.')].strip().isalnum():
                        index = row.find('.')
                        row = row[:index-1].replace('    ', '\t')+''+row[index-1:]
                        # TODO: 返回结果
                        self.result.append(None)
                else:
                    self.stop = False
                    self.mode = 'normal'
                    self.result.append(self.row_process(row))
            self.file += row+'\n'

    @staticmethod
    def format(file) -> str:
        """
        重新格式化

        :type file: io.TextIO
        :return: string
        """

        format_file = ''
        for string in file.readlines():
            if not string.strip():
                # format_file += str(string)
                pass
            # elif string[0] == '\t' or string[:4] == '    ':
            #     format_file += str('\t' + string[1 if string[0] == "\t" else 4:])
            else:
                # 将四个以下连续空格去除 四个连续空格替换成一个空格
                string = string.replace('   ', '\t').strip('\t')
                if string[0] in ['#', '>']:
                    string = string.split(' ')
                    if string[0][-1] == '#':
                        if len(string) != 1:
                            format_file += str(' '.join(string))
                    elif string[0][-1] == '>':
                        string = ' '.join(string)
                        for index, char in enumerate(string):
                            if char != '>' and char != ' ':
                                char = string[:index].replace(' ', '')
                                string = string[index:]
                                format_file += str(char + ' ' + string)
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
                                format_file += str(tag * index + ' ' + string)
                                break
                else:
                    format_file += str(string)
        return format_file

    def load(self, string):
        """ 加载器 --> 数据实时返回"""
        pass


# 处理 HTML 标记
class HTML(Base):
    def __init__(self):
        super().__init__()
