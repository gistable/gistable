#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<i@binux.me>
#         http://binux.me
# Created on 2013-03-02 20:47:08

import os
import re
import sys
import logging
import requests
from PIL import Image

class PinterestAPI(object):
    def __init__(self):
        self.origin = 'http://pinterest.com'
        self.ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.19 Safari/537.31'

    @property
    def headers(self):
        return {'Cookie': self.cookie,
                'Origin': self.origin,
                'User-Agent': self.ua, }

    def login(self, cookie=None):
        if not cookie:
            cookie = raw_input('Cookie: ')
        self.cookie = cookie
        self.csrf = re.search('csrftoken=(\w+)', cookie).group(1)

    def bookmark(self, board, caption, media_url, url):
        data = {
                'title': 'Create New Board',
                'board': board,
                'caption': caption,
                'tags': '',
                'replies': '',
                'buyable': '',
                'media_url': media_url,
                'url': url,
                'via': '',
                'csrfmiddlewaretoken': self.csrf,
                'form_url': '/pin/create/bookmarklet/',
                }
        return requests.post('http://pinterest.com/pin/create/bookmarklet/',
                                data=data, headers=self.headers)

    def add(self, board, caption, media_url, url):
        data = {
                'board': str(board),
                'details': caption,
                'link': url,
                'img_url': media_url,
                'tags': '',
                'replies': '',
                'buyable': '',
                'csrfmiddlewaretoken': self.csrf,
                }
        return requests.post('http://pinterest.com/pin/create/',
                                data=data, files={}, headers=self.headers)

    def upload(self, board, caption, img):
        if isinstance(img, basestring):
            img = open(img)
        data = {
                'board': str(board),
                'details': caption,
                'link': '',
                'img_url': '',
                'tags': '',
                'replies': '',
                'buyable': '',
                'csrfmiddlewaretoken': self.csrf,
                }
        return requests.post('http://pinterest.com/pin/create/',
                                data=data, files={'img': img}, headers=self.headers)

danbooru_re = re.compile(r'(\w{32})\.[png|jpg|jpeg]')
yande_re = re.compile(r'yande.re (\d+)')
konachan_re = re.compile(r'Konachan.com - (\d+)')
def do(api, board_id, filename):
    if yande_re.match(filename):
        m = yande_re.match(filename)
        data = requests.get('https://yande.re/post.json?tags=id:%s' % m.group(1)).json
        assert api.add(board_id, data[0]['tags'], data[0]['file_url'], 'https://yande.re/post/show/%s/' % data[0]['id']).ok
    elif konachan_re.match(filename):
        m = konachan_re.match(filename)
        data = requests.get('http://konachan.com/post.json?tags=id:%s' % m.group(1)).json
        assert api.add(board_id, data[0]['tags'], data[0]['file_url'], 'http://konachan.com/post/show/%s/' % data[0]['id']).ok
    elif danbooru_re.match(filename):
        m = danbooru_re.match(filename)
        data = requests.get('http://danbooru.donmai.us/posts.json?tags=md5:%s' % m.group(1)).json
        assert api.add(board_id, data[0]['tag_string'], 'http://danbooru.donmai.us/data/%s.%s' % (data[0]['md5'], data[0]['file_ext']), 'http://danbooru.donmai.us/posts/%s' % data[0]['id']).ok
    else:
        assert api.upload(board_id, filename, os.path.join(sys.argv[1], filename)).ok

if __name__ == '__main__':
    api = PinterestAPI()
    api.login('copy your cookie here')
    board_id = xxxxxxxxxxxx # open one of your board page find <ul class="BoardListUl"> and fill the data here from source code.

    for filename in os.listdir(sys.argv[1]):
        try:
            Image.open(os.path.join(sys.argv[1], filename))
        except:
            print filename, 'not image'
            continue

        try:
            do(api, board_id, filename)
        except Exception, e:
            logging.exception(filename)
            try:
                api.upload(board_id, filename, os.path.join(sys.argv[1], filename))
            except Exception, e:
                logging.exception(filename)
                continue
        print filename, 'ok!'
