# Coding: UTF-8
# Author: 尘
# Datetime: 2021/8/3
# instructions: 依赖： pillow_heif  pillow-avif-plugin
# 图片浏览器 https://interversehq.com/qview/download/
# 使用说明: 实例化Downloader然后调用.download即可

import signal
import lib
import requests
import warnings
from lib.threadpool import ThreadPool
import os
from io import BytesIO
import json
from PIL import UnidentifiedImageError, Image


def save_file(fileurl, filepath):
    """必须开启vpn专家(无360)模式,解决了urlretrieve 403的问题"""
    s = requests.Session()
    s.trust_env = False  # 使用VPN时必须加这句话!!!否则check_hostname requires server_hostname
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36'}
    res = s.get(fileurl, headers=head)
    # 直接保存
    # with open(filepath + '.jpg', 'wb') as fp:
    #     fp.write(res.content)
    # PIL不能直接读返回数据，需要将Bytes转IO流
    im: Image.Image = Image.open(BytesIO(res.content))
    try:
        im.save(lib.del_suffix(filepath) + '.jpg', 'jpeg')
    except OSError:
        im.save(lib.del_suffix(filepath) + '.png', 'png')


class Downloader:
    def __init__(self, save_to, max_workers=8, set_monitor=True, debug=False, img_format='avif', quantity=95):
        self.debug = debug  # 开启后打印错误信息
        self.max_workers = max_workers
        self.save_to = save_to
        self.success_count = 0
        self.task_count = 0
        self.exist_count = 0
        self.img_format = img_format
        self.quantity = quantity  # 保存图片的质量，默认95，
        self.close = self.shutdown

        if img_format == 'avif':
            try:
                import pillow_avif  # 开启avif支持
            except ImportError:
                self.img_format = 'jpeg'
                warnings.warn('未安装 pillow-avif-plugin包，不能保存为AVIF格式')
        elif img_format == 'jpg':
            self.img_format = 'jpeg'

        if not os.path.exists('下载记录.json'):
            with open('下载记录.json', 'w', encoding='utf-8') as f:
                json.dump({}, f)
        with open('下载记录.json', 'r+', encoding='utf-8') as f:
            self.record = json.load(f)

        self.pool = ThreadPool(self.max_workers)
        if set_monitor:
            self.pool.set_monitor()  # 启动线程池监视(进度条)

        signal.signal(signal.SIGINT, self.shutdown_now)  # 监听CTRL+C事件

        # 检查文件目录
        try:
            os.mkdir(save_to)
        except FileExistsError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    def shutdown_now(self, *parms):
        print('\n=========用户强制退出=========')
        with open('下载记录.json', 'w', encoding='utf-8') as f:
            json.dump(self.record, f)
        print(f'本次下载 累计：{self.task_count}，成功：{self.success_count}，已存在：{self.exist_count}')
        self.pool.shutdown_now()

    def shutdown(self):
        """必须调用该函数退出!"""
        excs = self.pool.shutdown()
        print('\n=========下载完成=========')
        with open('下载记录.json', 'w', encoding='utf-8') as f:
            json.dump(self.record, f)
        print(f'本次下载 累计：{self.task_count}，成功：{self.success_count}，已存在：{self.exist_count}')
        if len(excs) > 0:
            print('失败url如下：')
            if self.debug:
                print('debug开启')
                for exc in excs:
                    print(exc)
            else:
                for exc in excs:
                    print(exc[1])

    @staticmethod
    def url_standardize(url: str):
        """url标准化
        去除url中@/?后字符，间接修正webp和垃圾下载器问题
        """
        if url[:2] == '//':
            url = 'https:' + url
        return url.split(sep='?')[0].split(sep='@')[0]

    def save_img(self, fileurl):
        """
        优先存为jpg格式，如有透明通道存png
        """
        fileurl = self.url_standardize(fileurl)

        s = requests.Session()
        s.trust_env = False  # 使用VPN时必须加这句话!!!否则check_hostname requires server_hostname
        head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/92.0.4515.107 Safari/537.36'}
        res = s.get(fileurl, headers=head)  # 下载
        # PIL不能直接读返回数据，需要将Bytes转IO流
        try:
            im: Image.Image = Image.open(BytesIO(res.content))
            if im.width == 0:
                raise UnidentifiedImageError
        except UnidentifiedImageError:
            # 下载失败/非图片
            raise Exception('下载失败或者非图片url')

        dhash = lib.dhash(im)
        filepath = os.path.join(self.save_to, dhash)

        try:
            # 在索引块record[dhash[:2]]查找是否下载过，如已下载函数返回(dhash[:2]是索引)
            if dhash in self.record[dhash[:2]]:
                self.exist_count += 1
                return
        except KeyError:
            pass
        try:
            im.save(filepath + f'.{self.img_format}', format=self.img_format)
        except OSError:
            im.save(filepath + '.png', format='png')
        # 根据索引写入下载记录到变量（分块索引）
        self.record.setdefault(dhash[:2], []).append(dhash)
        self.success_count += 1
        return

    def download(self, urls):
        if isinstance(urls, str):
            # 只有一个url
            urls = [urls, ]
        assert isinstance(urls, list)

        self.task_count += len(urls)
        for fileurl in urls:
            self.pool.submit(self.save_img, fileurl)
        return self


if __name__ == '__main__':
    pass
