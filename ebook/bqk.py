#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests  # 用来抓取网页的html源码
import random  # 取随机数
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import sys
import os
import time  # 时间相关操作


class downloader(object):
    def __init__(self):
        self.server = 'https://www.biqukan.com'
        self.target = 'https://www.biqukan.com/1_1680/'
        self.title = ''  # 书名
        self.names = []  # 章节名
        self.urls = []  # 章节链接
        self.nums = 0  # 章节数
        self.download_page = 20  # 下载多少章
        self.filter_text = [
            '请记住本书首发域名：www.biqukan.com。笔趣阁手机版阅读网址：wap.biqukan.com',
            '()'
        ]

    """
    获取html文档内容
    """

    def get_content(self, url):
        # 设置headers是为了模拟浏览器访问 否则的话可能会被拒绝 可通过浏览器获取
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.biqukan.com',
            'If-Modified-Since': 'Tue, 10 Dec 2019 10:55:31 GMT',
            'If-None-Match': 'W/"5def79a3-141a7"',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        }

        # 设置一个超时时间 取随机数 是为了防止网站被认定为爬虫
        timeout = random.choice(range(80, 180))

        while True:
            try:
                # req = requests.get(url=url,headers=header,  timeout=timeout)
                req = requests.get(url=url, timeout=timeout)
                break
            except Exception as e:
                print('3', e)
                time.sleep(random.choice(range(8, 15)))

        # print(req.content.decode('utf-8'))
        # exit()
        # print(req.text)
        return req.content

    """
    获取下载的章节目录
    """

    def get_download_catalogue(self, url):
        print(url)
        html = self.get_content(url)

        print(html)

        bf = BeautifulSoup(html, 'html.parser')

        self.title = bf.find('h2').get_text() + '.txt'

        print('find:%s' % self.title)

        texts = bf.find_all('div', {'class': 'listmain'})

        print(texts)
        exit()

        div = texts[0]
        a_s = div.find_all('a')
        download_page = self.download_page
        self.nums = len(a_s[12:download_page])  # 我们需要去掉重复的最新章节列表 只为演示 我们只取 不重复的前5章
        for each in a_s[12:download_page]:
            print('find:%s' % each.string)
            self.names.append(each.string)
            self.urls.append(self.server + each.get('href'))

    """
    获取下载的具体章节
    """

    def get_download_content(self, url):
        html = self.get_content(url)

        bf = BeautifulSoup(html, 'html.parser')

        [s.extract() for s in bf('script')]

        text = bf.find('div', {'class': 'showtxt', 'id': 'content'}).get_text().strip()

        text = text.replace('\xa0' * 7, '\n\n').replace(url, '')  # \xa0表示连续的空白格

        for t in self.filter_text:
            text = text.replace(t, '')

        return text

    """
    将文章写入文件
    """

    def writer(self, name, path, text):
        write_flag = True
        with open(path, 'a', encoding='utf-8') as f:
            f.write(name + '\n')
            f.writelines(text)
            f.write('\n\n')


if __name__ == '__main__':
    dl = downloader()
    dl.get_download_catalogue(dl.target)
    if os.path.exists(dl.title):
        os.remove(dl.title)
    for i in range(dl.nums):
        dl.writer(dl.names[i], dl.title, dl.get_download_content(dl.urls[i]))
        print("已下载：%.2f%%" % float((i + 1) / dl.nums * 100) + '\r')
    print('下载完成！')
