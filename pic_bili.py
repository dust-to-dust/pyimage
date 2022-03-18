# coding: UTF-8
# Author: 尘
# Datetime: 2021/9/16 
# Instructions:


import lib
import re


def parse_dynamic(uid=0, dynamic_url='', offset_dynamic_id='', max_depth=8) -> list:
    """

    @param uid: 用户id  int/str
    @param dynamic_url: 动态页链接，用于解析uid，优先级高于uid
    @param offset_dynamic_id: 内部变量，动态id偏移
    @param max_depth: 最大迭代深度，每迭代一次获取12条动态
    @return: 解析到的图片urls
    """
    assert uid or dynamic_url
    if max_depth <= 0:
        return []
    if dynamic_url != '':
        uid = lib.parse_int(dynamic_url)
    url = f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?visitor_uid=10330740' \
          f'&host_uid={uid}&offset_dynamic_id={offset_dynamic_id}&need_top=1&platform=web '
    res = lib.get_json(url)
    try:
        res = str(res['data']['cards'])
    except KeyError:
        # 已经获取所有动态，结束递归
        return []
    # print(len(res))     # 12
    imgurls_ori = re.findall(re.compile('"img_src":"(.*?)"'), res)
    last_dynamic_id = re.findall(re.compile("'dynamic_id': (.*?),"), res)[-1]
    imgurls = [imgurl.replace(r'\\', '') for imgurl in imgurls_ori]
    imgurls.extend(parse_dynamic(uid, '', last_dynamic_id, max_depth - 1))
    return imgurls


def parse_article(uid=0, article_url='', pages=10) -> list:
    """

    @param uid: 用户id  int/str
    @param article_url: 专栏页链接，用于解析uid，优先级高于uid
    @param pages: 解析多少页专栏，每页是30条文章
    @return: 解析到的图片urls
    """
    assert uid or article_url

    if article_url != '':
        uid = lib.parse_int(article_url)

    imgurls = []
    for page in range(1, pages + 1):
        url = f'https://api.bilibili.com/x/space/article?mid={uid}&pn={page}&ps=30&sort=publish_time&jsonp=jsonp'
        res = lib.get_json(url)
        try:
            articles = res['data']['articles']
        except KeyError:
            # 已经获取所有文章，退出循环
            break
        else:
            for article in articles:
                aid = article['id']
                imgurls_ = lib.parse_img(f'https://www.bilibili.com/read/cv{aid}')
                imgurls.extend(['https:' + url for url in imgurls_])

    return imgurls


if __name__ == '__main__':
    with lib.Downloader('./bili', debug=True) as d:
        parser = lib.Parser()
        d.download(parser.parse_img('https://www.bilibili.com/read/cv7728476'))     # 解析专栏子页
        d.download(parse_article(uid=414702361))   # 通过uid解析专栏
        d.download(parse_dynamic(dynamic_url='https://space.bilibili.com/610810838/dynamic'))   # 通过url解析动态

