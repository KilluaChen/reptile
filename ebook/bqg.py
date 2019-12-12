#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests  # 用来抓取网页的html源码
import random  # 取随机数
from bs4 import BeautifulSoup  # 用于代替正则式 取源码中相应标签中的内容
import sys
import os
import time  # 时间相关操作
from threading import Thread
import re


class downloader(object):

    def async2(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()

        return wrapper

    def __init__(self):
        self.server = 'https://www.xbiqugexsw.com'
        self.target = 'https://www.xbiqugexsw.com/book/188380'
        self.names = []  # 章节名
        self.urls = []  # 章节链接
        self.start_nums = 1  # 从第几章开始下载
        self.dl_nums = 1  # 下载多少章 None 下载全部
        self.contents = []  # 章节内容
        self.filter_text = [
            '转码页面功能异常，本站不支持转码阅读，点击页面底部[查看原网页]可正常浏览，或通过浏览器访问本页地址: http://www.xbiqugexsw.com/',
            '本站重要通知:请使用本站的免费小说APP,无广告、破防盗版、更新快,会员同步书架,请关注微信公众号　appxsyd　(按住三秒复制)　下载免费阅读器!!',
            '如果您中途有事离开，请按CTRL+D键保存当前页面至收藏夹，以便以后接着观看！',
            '()',
            '本章未完，点击下一页继续阅读',
            '-->>',
            '　　;',
            '[]',
            '>　　',
            '...　　...',
            'r',
        ]

    """
    获取html文档内容
    """

    def get_content(self, url):
        while True:
            try:
                header = {
                    'authority': 'www.xbiqugexsw.com',
                    'method': 'GET',
                    'path': '/book/62009/1.html',
                    'scheme': 'https',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'cookie': '__cfduid=dd342cdbe2e7283aa1e2420259cb75bea1576034420; PHPSESSID=uik927s0muo5b11kvciuc56rg3; viewed_page_cnt=24_Wed, 11 Dec 2019 11:20:38 GMT',
                    'referer': 'https://www.xbiqugexsw.com/book/62009/',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade - insecure - requests': '1',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
                }
                return requests.get(url=url, timeout=5, headers=header).content.decode('utf-8')
            except Exception as e:
                print('下载失败,正在重试...', e)

    """
    获取下载的章节目录
    """

    def get_download_catalogue(self, url):
        print(url)

        html = self.get_content(url)
        bf = BeautifulSoup(html, 'html.parser')
        self.title = bf.find('h1').get_text() + '.txt'
        print('find:%s' % self.title)

        list = bf.find_all('dd')

        for item in list[13:]:
            a = item.find('a')
            print('find:' + a.string)
            self.urls.append(a.get('href'))
            self.names.append(a.string)

        if not dl.dl_nums:
            self.dl_nums = len(self.urls) + 1
        if not self.urls:
            print('章节获取失败')
            exit()

    @async2
    def start_download(self, index):
        self._get_content(index)
        pass

    """
    获取下载的具体章节
    """

    def _get_content(self, index, url=False):
        if not url:
            url = self.urls[index]
        name = self.names[index]
        html = self.get_content(self.server + url)

        bf = BeautifulSoup(html, 'html.parser')

        text = bf.find('div', {'id': 'content'}).get_text().strip()
        text = re.sub(u'((http|手机用户).*[a-zA-Z0-9]+)', '', text)
        text = text.replace('\xa0' * 7, '\n\n').replace(url, '').replace('　　', '\n\n')  # \xa0表示连续的空白格

        for t in self.filter_text:
            text = text.replace(t, '')

        next = bf.find('p', {'class': 'to_nextpage'})
        if next:
            next_section_url = bf.find('p', {'class': 'to_nextpage'}).find('a').get('href')
            if next_section_url:
                text = text + self._get_content(index, next_section_url)
                text = name + '\n' + text
                self.contents.insert(index, {'sort': index + 1, 'text': text})
                print('当前进度%.2f%%,成功下载:%s' % (float(len(self.contents) / dl.dl_nums * 100), name))
                current_len = len(self.contents)
                if current_len == self.dl_nums:
                    print('下载完成,耗时:%s秒,开始写入文件' % int((time.time() - self.start)))
                    self.contents = sorted(self.contents, key=lambda x: x['sort'])
                    for x in self.contents:
                        self.writer(x['text'])
                    print('===>文件写入完成:%s<===' % self.title)
        return text

    """
    将文章写入文件
    """

    def writer(self, text):
        write_flag = True
        with open(self.title, 'a', encoding='utf-8') as f:
            f.writelines(text)
            f.write('\n\n')


if __name__ == '__main__':

    start = time.time()
    dl = downloader()
    dl.start = start
    dl.get_download_catalogue(dl.target)
    if os.path.exists(dl.title):
        os.remove(dl.title)
        print('文件已存在,删除成功')

    total_nums = len(dl.urls)
    for i in range(total_nums):
        if i <= dl.start_nums:
            continue
        if i > dl.start_nums + dl.dl_nums:
            break
        dl.start_download(i)
