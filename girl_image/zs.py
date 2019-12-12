import urllib.request
import os
import re
from threading import Thread

page = 0


# 多线程
def async2(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


# 获取图片列表
def find_images(url):
    global page
    page += 1
    if page > 2:
        return
    print('开始下载第%s页' % page)
    res = urllib.request.urlopen(url)
    html = res.read().decode('utf-8')

    # 设置目录
    folder = os.getcwd() + '/images/' + get_current_page(html)
    if not os.path.exists(folder):
        os.mkdir(folder)

    # 下载图片
    pattern = r'<img src="([^"]+\.jpg)"'
    img_list = re.findall(pattern, html)
    download_img(img_list, folder)

    # 下一页
    next_url = get_next_url(html)
    find_images(next_url)
    pass


# 获取当前页码
def get_current_page(html):
    pattern = r'<span class="current-comment-page">\[([\s\S]*?)\]'
    list = re.findall(pattern, html)
    return list[0]
    pass


# 获取下一页地址
def get_next_url(html):
    pattern = r'<a title="Older Comments" href="([\s\S]*?) class="previous-comment-page"'
    list = re.findall(pattern, html)
    if not list:
        print('已到底部,停止下载')
        exit()
    return 'http:' + list[0].replace('#comments', '')
    pass


# 下载图片
@async2
def download_img(image_list, folder):
    for url in image_list:
        filename = folder + '/' + url.split('/')[-1]
        urllib.request.urlretrieve('http:' + url, filename=filename)
        print('下载图片:%s' % filename)
    pass


if not os.path.exists('images'):
    os.mkdir('images')
find_images('http://jandan.net/ooxx')
