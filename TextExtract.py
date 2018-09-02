# -*- coding: utf-8 -*-
# @File    : TextExtract.py
# @Author  : LVFANGFANG
# @Time    : 2018/8/5 0005 19:15
# @Desc    : 基于行块分布函数的通用网页正文抽取算法

import re
import time
import traceback
import html

import requests


class TextExtract:
    __text = []
    __indexDistribution = []

    def __init__(self, threshold=86, blocksWidth=3):
        self.threshold = threshold
        self.blocksWidth = blocksWidth

    def parse(self):
        self.preProcess()
        return self.getText()

    def preProcess(self):
        regex = re.compile(
            r'<!DOCTYPE.*?>|'
            r'<!--[\s\S]*?-->|'
            r'<script.*?>.*?</script>|'
            r'<style.*?>.*?</style>|'
            r'<.*?>', re.S | re.I
        )
        # re_char = re.compile(r'&#?.{2,6};', re.S | re.I)
        self.html = regex.sub('', self.html)
        self.html = html.unescape(self.html)

    def getText(self):
        self.__text.clear()
        self.__indexDistribution.clear()
        lines = list(map(lambda x: re.sub('\s+', '', x), self.html.split('\n')))
        self.__indexDistribution = self.computeIndexDistribution(lines)
        # print(self.__indexDistribution)

        start = -1
        end = -1
        boolstart = False
        boolend = False

        for i in range(len(self.__indexDistribution) - 1):
            if self.__indexDistribution[i] > self.threshold and (not boolstart):
                if self.__indexDistribution[i + 1] or self.__indexDistribution[i + 2] or self.__indexDistribution[
                            i + 3]:
                    boolstart = True
                    start = i
                    continue
            if boolstart:
                if self.__indexDistribution[i] == 0 or self.__indexDistribution[i + 1] == 0:
                    end = i
                    boolend = True
            if boolend:
                tmp = [i for i in lines[start:end + 1] if len(i) >= 2]
                # tmp = [i for i in lines[start:end + 1]]
                s = '\n'.join(tmp)
                if 'Copyrigh' in s or '版权所有' in s:
                    continue
                self.__text.append(s)
                boolstart = boolend = False
        if not self.__text:
            print('xxxxxx无正文xxxxxx')
        else:
            # result = ''.join(self.__text)
            result = max(self.__text, key=lambda x: len(x))
            return result

    def computeIndexDistribution(self, lines):
        indexDistribution = []
        for i in range(len(lines) - self.blocksWidth):
            wordsNum = 0
            for j in range(i, i + self.blocksWidth):
                wordsNum += len(lines[j])
            indexDistribution.append(wordsNum)
        return indexDistribution

    def getHtml(self, url, retry=3):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36'}
        while retry:
            try:
                response = requests.get(url, headers=headers)
                break
            except Exception as e:
                traceback.print_exc()
                time.sleep(3)
                retry -= 1
        response.encoding = response.apparent_encoding
        self.html = response.text
        # print(self.html)


if __name__ == '__main__':
    url = 'http://news.enorth.com.cn/system/2018/07/13/035824255.shtml'
    extractor = TextExtract(threshold=86, blocksWidth=3)
    extractor.getHtml(url)
    print(extractor.parse())
