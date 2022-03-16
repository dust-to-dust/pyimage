# Coding: UTF-8
# Author: 尘
# Datetime: 2021/8/3 
# 使用说明: 实例化Downloader然后调用.download
import logging

import lib
import requests
from lib.threadpool import ThreadPool
import os
from PIL import Image
from io import BytesIO
import json


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
    def __init__(self, save_to, max_workers=8, set_monitor=True, debug=False):
        self.debug = debug  # 开启后打印错误信息
        self.max_workers = max_workers
        self.save_to = save_to
        self.success_count = 0
        self.task_count = 0
        self.exist_count = 0
        self.log = self.setLog()
        self.close = self.shutdown

        with open('下载记录.json', 'r+', encoding='utf-8') as f:
            self.record = json.load(f)
        self.pool = ThreadPool(self.max_workers)
        if set_monitor:
            self.pool.set_monitor()     # 启动线程池监视(进度条)

        # 检查文件目录
        try:
            os.mkdir(save_to)
        except FileExistsError:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @staticmethod
    def setLog():
        # todo
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(f"日志.log", mode="a+", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("[%(asctime)s][%(pathname)s-line:%(lineno)d][%(levelname)s]\n%(funcName)s —— %(message)s")
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(
            logging.Formatter("[%(levelname)s]\n%(funcName)s —— %(message)s")
        )
        stream_handler.setLevel(logging.DEBUG)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger

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
    def url_standardize(url):
        """url标准化
        去除url中@/?后字符，间接修正webp和垃圾下载器问题
        """
        return url.split(sep='?')[0].split(sep='@')[0]

    @staticmethod
    def get_id(url: str):
        """截取url末尾至多30位作为id"""
        id_ = url.split('/')[-1]
        if len(id_) > 30:
            return id_[len(id_) - 30:]
        else:
            return id_

    def save_img(self, fileurl):
        """
        必须开启vpn专家(无360)模式,解决了urlretrieve 403的问题
        优先存为jpg格式，如有透明通道存png
        """
        id_ = self.get_id(fileurl)
        try:
            # 在索引块record[filename[0]]查找是否下载过，如已下载函数返回
            if id_ in self.record[id_[0]]:
                self.exist_count += 1
                return
        except KeyError:
            pass

        s = requests.Session()
        s.trust_env = False  # 使用VPN时必须加这句话!!!否则check_hostname requires server_hostname
        head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/92.0.4515.107 Safari/537.36'}
        res = s.get(fileurl, headers=head)
        # PIL不能直接读返回数据，需要将Bytes转IO流
        im: Image.Image = Image.open(BytesIO(res.content))
        try:
            im.save(os.path.join(self.save_to, lib.del_suffix(id_) + '.jpg'), 'jpeg')
        except OSError:
            im.save(os.path.join(self.save_to, lib.del_suffix(id_) + '.png'), 'png')
        # 根据索引写入下载记录到变量（分块索引）
        self.record.setdefault(id_[0], []).append(id_)
        self.success_count += 1
        return

    def download(self, urls):
        if isinstance(urls, str):
            # 只有一个url
            urls = [urls, ]
        assert isinstance(urls, list)
        self.task_count += len(urls)
        for fileurl in urls:
            fileurl = self.url_standardize(fileurl)
            self.pool.submit(self.save_img, fileurl)
        return self


if __name__ == '__main__':
    pass

