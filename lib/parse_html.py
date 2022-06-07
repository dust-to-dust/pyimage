# Coding: UTF-8
# Author: 尘
# Datetime: 2021/8/13 
# DebugInfo:

from selenium import webdriver
import requests
from lxml import etree
from hashlib import md5


class Parser:
    def __init__(self, domain=None, proxies=None, ajax: bool = False, cookie=None):
        """
        :domain: 用于补全相对链接
        :proxies: 设置代理，eg(西部世界)：{
            "http": "http://127.0.0.1:21882",
            "https": "http://127.0.0.1:21882",
        }
        :ajax: 目标内容是否异步加载
        :cookie: cookie字典
        """
        self.timeout = 8
        self.domain = domain
        self.ajax = ajax
        self.imgurls = []
        self.session = requests.session()
        self.session.max_redirects = 5
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3861.400 QQBrowser/10.7.4313.400'}
        if proxies:
            self.session.proxies = proxies
        if cookie:
            self.session.cookies = cookie
        if ajax:
            self.browser = webdriver.Chrome('./chromedriver.exe')  # 创建浏览器控制对象,并启动浏览器
            self.browser.implicitly_wait(5)  # 最大等待响应时间，对所有操作有效，重新执行间隔0.5s

    def url_standardize(self, url: str):
        if url[:2] == '//':
            url = 'https:' + url
        elif url[0] == '/':
            url = self.domain + url
        return url

    def parse(self, url, xpath, html='') -> list:
        assert url or html  # url和html二选一

        if url:
            url = self.url_standardize(url)
        if isinstance(xpath, str):
            xpath = [xpath]

        imgurls = []
        if self.ajax:
            assert url
            self.browser.get(url)  # 打开网页
            for xp in xpath:
                imgurls.extend(self.browser.find_elements_by_xpath(xp))
        else:
            if not html:
                html = self.session.get(url=url, timeout=self.timeout).text
            doc = etree.HTML(html)
            for xp in xpath:
                imgurls.extend(doc.xpath(xp))
        return imgurls

    def parse_img(self, url, html: str = '') -> list:
        return self.parse(url, ['//img/@src', '//img/@data-src'], html)

    @staticmethod
    def parse_cookie(cookie: str):
        """cookie含中文会报错"""
        cookies = {}  # 初始化cookies字典变量
        for line in cookie.split(';'):  # 按照字符：进行划分读取
            # 其设置为1就会把字符串拆分成2份
            name, value = line.strip().split('=', 1)
            cookies[name] = value  # 为字典cookies添加内容
        return cookies

    @staticmethod
    def parse_cn(string: str):
        """处理中文乱码"""
        return string.encode('iso-8859-1').decode('gbk')

    @staticmethod
    def parse_int(string: str):
        return int(''.join([x for x in string if x.isdigit()]))


def get_html(url):
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36'}
    return requests.get(url, headers=head).text


def get_json(url):
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36'}
    return requests.get(url, headers=head).json()


def parse_img(url):
    doc = etree.HTML(requests.get(url).text)
    imgurls = doc.xpath('//img/@src')
    if not imgurls:
        imgurls = doc.xpath('//img/@data-src')

    return imgurls


def parse_cookie(cookie: str):
    """cookie含中文会报错"""
    cookies = {}  # 初始化cookies字典变量
    for line in cookie.split(';'):  # 按照字符：进行划分读取
        # 其设置为1就会把字符串拆分成2份
        name, value = line.strip().split('=', 1)
        cookies[name] = value  # 为字典cookies添加内容
    return cookies


def parse_cn(string: str):
    """处理中文乱码"""
    return string.encode('iso-8859-1').decode('gbk')


def parse_int(string: str):
    return int(''.join([x for x in string if x.isdigit()]))


class Chaojiying(object):
    # 超级鹰验证码平台处理代码，未测试
    # 来源：https://www.jianshu.com/p/4097b4d35f9f
    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,  # 用户名
            'pass2': self.password,  # 用户密码
            'softid': self.soft_id,  # 软件ID，在用户中心->软件ID->自己生成
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def post_pic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files,
                          headers=self.headers)
        return r.json()

    def report_error(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    pass
