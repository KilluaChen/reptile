import urllib.request
import os
from threading import Thread
from bs4 import BeautifulSoup

page = 0
count = 0


# 多线程
def async2(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper
    pass


# 获取图片列表
def find_images(url):
    global page
    page += 1
    # if page > 2:
    #     return
    print('开始下载第%s页' % page)
    res = urllib.request.urlopen(url)
    html = res.read().decode('utf-8')
    bs = BeautifulSoup(html, 'html.parser')

    # 设置目录
    cu_page = bs.find('span', {'class': 'current-comment-page'}).get_text().replace('[', '').replace(']', '')
    folder = os.getcwd() + '/images/' + cu_page
    if not os.path.exists(folder):
        os.mkdir(folder)

    # 下载图片
    img_list = bs.find_all('img', {'referrerpolicy': 'no-referrer'})
    download_img(img_list, folder)

    # 下一页
    next = bs.find('a', {'class': 'previous-comment-page'})
    if next:
        find_images('http:' + next.get('href'))
    pass


# 下载图片
@async2
def download_img(image_list, folder):
    for url in image_list:
        url = 'http:' + url.get('src')
        global count
        count = count + 1
        print('下载图片:%s url:%s' % (count, url))
        filename = folder + '/' + url.split('/')[-1]
        urllib.request.urlretrieve(url, filename=filename)
    pass


if not os.path.exists('images'):
    os.mkdir('images')
find_images('http://jandan.net/ooxx')
