# !/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
from urlparse import urlparse, parse_qs

import requests


def getappmsgext(key, uin, url):
    """
    :param key: 访问者的秘钥
    :param uin: 访问者的ID（base64编码）
    :param url: 需要抓取的文章链接
    :return: 
    """
    qs = dict((k, v if len(v) > 1 else v[0])
              for k, v in parse_qs(urlparse(url).query).iteritems())
    params = {
        "__biz": qs.get('__biz'),
        "mid": qs.get('mid'),
        "sn": qs.get('sn'),
        "idx": qs.get('idx'),
        "f": "json",
        "is_need_ad": 0,
        "key": key,
        "uin": uin,
    }
    data = {
    	'is_only_read': 1,
    }
    api = 'http://mp.weixin.qq.com/mp/getappmsgext'
    resp = requests.post(api, headers=headers, params=params, data=data)
    json.dump(resp.json(), sys.stdout, indent=4, ensure_ascii=False)


article_url = 'https://mp.weixin.qq.com/s?__biz=MjM5NDAwMTA2MA==&mid=434466335&idx=1&sn=4b63bd2d8968487ad59abcf31b7c8b72'

"""
通过微信电脑版发起一个对话，粘贴以下URL发送，然后点击URL
1. 复制浏览器地址栏中的地址为key_url
2. 提取Cookie值wap_sid，设置为headers
https://mp.weixin.qq.com/s?__biz=MjM5NTE4Njc4NQ==&mid=405483849&idx=1&sn=cac39a93ea4058564cd81e6627060d2d#wechat_redirect
"""
headers = {
    'User-Agent': 'Version/4.0 Mobile Safari/533.1 MicroMessenger/4.5.255',
    'Cookie':'wap_sid=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
}
key_url = 'https://mp.weixin.qq.com/s?__biz=MjM5NTE4Njc4NQ==&mid=405483849&idx=1&sn=cac39a93ea4058564cd81e6627060d2d&uin=ODg4ODg4ODg%3D&key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx&devicetype=iMac+MacBook8%2C1+OSX+OSX+10.11.5+build(15F34)&version=11020201&lang=zh_CN&pass_ticket=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
qs = dict((k, v if len(v) > 1 else v[0]) for k, v in parse_qs(key_url).iteritems())
uin = qs.get('uin')
key = qs.get('key')

getappmsgext(key, uin, article_url)

"""
{
    ...
    "appmsgstat": {
        ...
        "read_num": 100001,
        "like_num": 2512
    }
}
"""
