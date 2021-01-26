# -*- coding: utf-8 -*-
# @Time     : 2021/1/22
# @Author   : hjhcos
# @File     : mk1.1.py
# @Project  : mark_app
# @Software : PyCharm
# =============================

import re


class Base(object):

    def __init__(self):
        self.RE = re.compile
        self.findall = re.findall
        self.search = re.search
        self.sub = re.sub
        self.tags = None
        self.patterns = None
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

    def __init__(self):
        super().__init__()
        self.tags = ('#', '>', '`', '$', '_', '*', '-', '~', '\\', '[', ']', '^', '(', ')', '|')
        self.patterns = (
            self.RE('`.*?`'),
            self.RE('\$.*?\$'),
            self.RE('_.*?_'),
            self.RE('\*.*?\*'),
            self.RE('--.*?-'),
            self.RE('~~.*?~~'),
            self.RE('\[.*?\].'),
            self.RE('^\|.*?\|.+\|$')
        )
        self.stop = False   # 是否停止样式检测的状态
        self.match = ''     # 匹配标记
        self.result = []    # 存放每段索引标记信息 [[['*', (start, end)], ['_', (start, end)]...], [['_', (start, end)]]]

    def division(self, string):
        """ 分割 ===》 内容与标记分割 只处理样式标签"""
        # print("MD.division", string)
        pass

    def detection(self, string):
        """ 检测 ===》 样式标记检测"""
        # TODO: 检测标记是否有无结尾符
        # print("MD.detection", string)
        # # > 已经做了处理不需要再进行处理
        # 这个循环是对数据里面是否存在标记进行预处理 没有则什么都不返回
        self.tags = ['*', '-', '_', '$', '`', '~']
        for tag in self.tags:
            if tag in string:
                break
            elif tag == self.tags[-1]:
                return

        match_tag = ''  # 当前标记
        matching = []   # 开始标记存放 待匹配
        matched = []    # 匹配到的标记
        # start = 0      # 标记内容开头索引
        # end = 0        # 标记内容结尾索引
        # TODO: 检测标记是否在同一行 除了 表格、代码块、数学公式以外 都在同一行
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
            self.division(matched)
            print(matched)
        pass

    def process(self, string):
        """ 处理器 ===》 内容分割、修复（标记、数据）"""
        co = string.strip()
        if not co:  # 防止没有字符串的情况 \n
            return '\n'
        string = co
        self.tags = ['#', '>', '`', '$', '-']
        # 处理开头字符是否符合前四个标记 符合就进行下一步处理

        if string[0] in self.tags:
            if string[0] in self.tags[:2]:
                # # > 内容分割 标记检测
                string = string.split(' ')
                if string[0][0] == '#':
                    tag = string[0]
                    string = ' '.join(string[1:])
                    self.detection(string)  # 返回格式 [['*', (start, end)]]   start 标记里面内容开头索引 end 标记里面内容结尾索引
                    pass
                else:
                    string = ''.join(string).split('>')
                    for length, tag in enumerate(string):
                        if tag or length+1 == len(string):
                            # 复原数据
                            if co[0] != co[1]:
                                tag = '> '*length
                            else:
                                tag = '>' * length
                            start = len(tag)
                            string = string[-1]
                            self.result.append([[tag, (start, None)]])
                            # self.result[-1]+self.detection(string)
                            self.detection(string)
                            break
            else:
                # TODO: 标记判别 `、$ 是否换行
                # TODO: 内部不需要进行其他样式识别
                # TODO: 换行可以获取到后面正确内容
                if string[0] == string[1]:
                    if string[:3] == '```':
                        ...
                    pass
                else:
                    self.detection(string)
        else:
            self.detection(string)

    def load(self, string):
        """ 加载器 ===》    数据实时返回"""
        pass


if __name__ == '__main__':
    with open('blog.md', 'r', encoding='utf-8') as fd:
        t = fd.read()
        t = t.split('\n')
    md = MD()

    for i in t:
        md.process(i)
