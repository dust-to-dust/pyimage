import os
from shutil import move  # 文件操作
import time
import lib
from selenium import webdriver
from lib.threadpool import ThreadPool
from lib.downloader import save_file
from lib.file_operate import is_img
import requests
# from collections import deque  # 栈
from selenium.webdriver.chrome.options import DesiredCapabilities

# 找到元素即下一步，不等待整个页面，参考https://blog.csdn.net/wkb342814892/article/details/81611737
DesiredCapabilities.CHROME["pageLoadStrategy"] = "none"


def search_ori_native(files_path='../pic', post_to='google'):
    # 初始化运行变量
    start = time.time()
    max_workers = 6
    files = []  # 文件名列表
    now = 0  # 当前处理文件下标
    finished = 0  # 成功完成数量
    timeout = 6  # 浏览器操作超时时间

    # 检查文件目录
    if not os.path.exists(files_path):
        print(f'将文件放入{files_path}后重新执行程序')
        os.mkdir(files_path)
        return
    try:
        os.mkdir(os.path.join(files_path, 'ori'))
        os.mkdir(os.path.join(files_path, 'finished'))
    except FileExistsError:
        pass

    for file in os.listdir(files_path):
        if is_img(file):
            files.append(file)
    if len(files) < max_workers:
        max_workers = len(files)

    if post_to in ['google', 'g', 'G']:
        def search_ori_mt(_file):
            _browser = webdriver.Chrome('../chromedriver.exe')  # 创建浏览器控制对象,并启动浏览器
            try:
                # 隐式等待，：对所有操作有效，重新执行间隔0.5s
                # 缺陷：程序会一直等待整个页面加载完成才会执行下一步，即使页面想要的元素已经加载完成
                _browser.implicitly_wait(timeout)  # 最大等待响应时间，
                # 提交文件
                _browser.get('https://www.google.com.hk/imghp?hl=zh-CN')  # get打开网页
                _browser.find_elements_by_css_selector('.jyfHyd')[1].click()  # 额外步骤--点击我同意
                # 点击相机图标
                _browser.find_element_by_css_selector('.tdPRye').click()
                _browser.find_element_by_css_selector('#awyMjb'). \
                    send_keys(os.path.join(os.path.abspath(files_path), _file))

                btn = _browser.find_elements_by_css_selector('.O1id0e a')[-1]  # 最大尺寸
                btn.click()

                items = _browser.find_elements_by_css_selector('#islrg img')  # 搜索结果图
                imgurl = ''
                flag = False
                for item in items[:6]:
                    item.click()

                    time.sleep(6)  # 等浏览器加载原图
                    for tag in _browser.find_elements_by_css_selector('.v4dQwb img'):
                        imgurl = tag.get_attribute('src')
                        if imgurl[:4] == 'http':
                            # 找到链接，退出
                            print(imgurl)
                            flag = True
                            break
                    if flag:
                        break

                if imgurl[:4] == 'data':
                    print('url解析出错', imgurl[:10])
                    return
                # 下载
                save_file(imgurl, os.path.join(files_path, 'ori', _file))
                # 移动原文件
                move(os.path.join(files_path, _file), os.path.join(files_path, 'finished', _file))
                nonlocal finished
                finished += 1
            # except urllib.error.URLError:
            #     print('网络连接错误 URLError')
            finally:
                _browser.quit()
    elif post_to in ['yande.re', 'y', 'Y']:
        def search_ori_mt(_file):
            _browser = webdriver.Chrome('../chromedriver.exe')  # 创建浏览器控制对象,并启动浏览器
            try:
                _browser.implicitly_wait(timeout)
                _browser.get('https://yande.re/post/similar')
                _browser.find_element_by_css_selector('#file') \
                    .send_keys(os.path.join(os.path.abspath(files_path), _file))
                _browser.find_element_by_xpath('//*[@id="similar-form"]/table/tfoot/tr/td/input').click()
                print(_browser.find_elements_by_xpath('//*[@id="post-list-posts"]/li/@id'))

            # -----------------------------------------------------------------------
            finally:
                _browser.quit()

    else:
        def search_ori_mt():
            pass

    with ThreadPool(max_workers) as pool:
        # 向空闲浏览器提交文件
        while now < len(files):
            # !!!TPE提交任务失败不会有任何提示，参数不需要括起来!!!
            pool.submit(search_ori_mt, files[now])
            now += 1

    print(f'本次完成数{finished}，失败数{len(files) - finished}，耗时{time.time() - start}')


def search_ori_by_url(url):
    # yande.re
    detail = 'https://yande.re/post/show/'
    data = {'commit': 'Search', 'url': url}
    html = requests.post(url='https://yande.re/post/similar', data=data).text

    parser = lib.Parser()
    # 遍历返回的id，解析尺寸最大的一张图的url
    id_list = parser.parse('', '//*[@id="post-list-posts"]/li/@id', html=html)[1:]
    if len(id_list) == 1:
        imgurl = parser.parse(detail + id_list[0], '//*[@id="highres"]/@href')
    elif len(id_list) > 1:
        size_list = []
        urls = []
        for id_ in id_list:
            id_ = id_[1:]  # 去掉打头的p
            # 详情页解析
            size = parser.parse(detail + id_, '//*[@id="stats"]/ul/li[3]/text()')
            imgurl = parser.parse(detail + id_, '//*[@id="highres"]/@href')
            # 解析图片size
            size_list.append(size[0][6:].split('x')[0])
            urls.append(imgurl[0])
        index = size_list.index(max(size_list))
        imgurl = urls[index]
    else:
        imgurl = ''
    return imgurl


if __name__ == '__main__':
    search_ori_native('../pic', 'y')


