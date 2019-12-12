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
        self.server = 'https://www.luocs.cn'
        self.target = 'https://www.luocs.cn/1/1670/'
        self.names = []  # 章节名
        self.urls = []  # 章节链接
        self.start_nums = 0  # 从第几章开始下载
        self.dl_nums = None  # 下载多少章 None 下载全部
        self.contents = []  # 章节内容
        self.folder = 'files/'
        self.filter_text = [
            '老规矩，日更，每天早上八点~很好养肥哒~小仙女们儿收藏来一发嘛o(*≧▽≦)ツ',
            '记住本站网址，Ｗｗｗ．luocs．Ｃn，方便下次阅读，或者百度输入“luocs.cn”，就能进入本站',
        ]

    """
    获取html文档内容
    """

    def get_content(self, url):
        while True:
            try:
                header = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Cookie': 'fikker-K1hS-2QXy=RGdkR9v7fabLtAFLRJ07v9IKBNb5jW61; fikker-K1hS-2QXy=RGdkR9v7fabLtAFLRJ07v9IKBNb5jW61',
                    'Host': 'www.luocs.cn',
                    'Referer': 'https://www.luocs.cn/1/1670/1596822.html',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
                }
                pro_ip = '121.69.46.177:9000'
                proxies = {
                    "http": "http://" + pro_ip,
                    "https": "http://" + pro_ip
                }
                content = requests.get(url=url, timeout=5, headers=header).content.decode('gbk')

                if '503 Service Temporarily Unavailable' in content:
                    raise RuntimeError('503 Service Temporarily Unavailable')

                return content
            except Exception as e:
                rand = random.randint(1, 10)
                print('下载失败... %s秒后重试! ' % (rand), e)
                time.sleep(rand)

    """
    获取下载的章节目录
    """

    def get_download_catalogue(self, url):
        print(url)

        html = self.get_content(url)
        bf = BeautifulSoup(html, 'html.parser')
        self.title = bf.find('h1').get_text() + '.txt'
        print('find:%s' % self.title)

        list = bf.find('div', {'class': 'article_texttitleb'}).find_all('a')

        for item in list:
            print('find:' + item.string)
            self.urls.append(item.get('href'))
            self.names.append(item.string)

        if not dl.dl_nums:
            self.dl_nums = len(self.urls)
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

    def _get_content(self, index):
        url = self.urls[index]
        name = self.names[index]
        html = self.get_content(self.server + url)
        bf = BeautifulSoup(html, 'html.parser')

        try:
            text = bf.find('div', {'id': 'book_text'}).get_text().strip()
            text = re.sub(u'((http|手机用户).*[a-zA-Z0-9]+)', '', text)
            text = text.replace('\xa0' * 7, '\n\n').replace(url, '').replace('　　', '\n\n')  # \xa0表示连续的空白格

            for t in self.filter_text:
                text = text.replace(t, '')

            text = name + '\n\n\t' + text
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

        except Exception as e:
            print(name, url, e)

    """
    将文章写入文件
    """

    def writer(self, text):
        write_flag = True
        with open(self.folder + self.title, 'a', encoding='utf-8') as f:
            f.writelines(text)
            f.write('\n\n')


if __name__ == '__main__':

    start = time.time()
    dl = downloader()
    dl.start = start
    dl.get_download_catalogue(dl.target)

    if not os.path.exists(dl.folder):
        os.mkdir(dl.folder)
        print('目录成功')
    if os.path.exists(dl.folder + dl.title):
        os.remove(dl.folder + dl.title)
        print('文件已存在,删除成功')

    total_nums = len(dl.urls) + 1
    for i in range(total_nums):
        if i <= dl.start_nums:
            continue
        if i > dl.start_nums + dl.dl_nums:
            break
        dl.start_download(i - 1)
        time.sleep(0.3)
