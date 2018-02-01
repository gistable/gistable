#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 1. 需要安装requests(pip3 install -U requests)
# 2. 需要crontab配合以辅助完成自动签到
# 3. 如果想使用自己的当前登录的Cookies
#    请在v2ex的浏览器控制台中输入
#    $.getScript('//cdn.rawgit.com/js-cookie/js-cookie/master/src/js.cookie.js', function() { console.log(JSON.stringify(Cookies.get())); })
#    替换V2EXGetReward.cookies文件中的相应的Cookies
#
# license: Public Domain
#
import json
import os
import re

import requests
from requests.utils import cookiejar_from_dict, dict_from_cookiejar


class V2EX:

    def __init__(self, username, password):
        self.cookies_path = os.path.realpath('$HOME/V2EXGetReward.cookies')
        self.username = username
        self.password = password
        self.session = requests.session()

    def sign_in(self):
        resp = self.session.get('https://www.v2ex.com/signin')
        once = re.search(r'value="(\d+)" name="once"', resp.text).group(1)
        self.session.post(
            url='https://www.v2ex.com/signin',
            data={'u': self.username, 'p': self.password, 'once': once, 'next': '/'},
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': resp.url
            }
        )

    def has_sign_in(self):
        resp = self.session.get('https://www.v2ex.com/')
        return 'signout' in resp.text

    def get_reward(self):
        resp = self.session.get('https://www.v2ex.com/mission/daily')
        if '\'/balance\'' in resp.text:
            return
        once = re.search(r'once=(\d+)\'', resp.text).group(1)
        self.session.get(
            url='https://www.v2ex.com/mission/daily/redeem?once=%s' % once,
            headers={'Referer': resp.url}
        )

    def cookies_load(self):
        data = {}
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, 'r') as fp:
                data = json.load(fp)
        if data and self.username in data:
            self.session.cookies.update(cookiejar_from_dict(data[self.username]))

    def cookies_save(self):
        data = {}
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, 'r') as fp:
                data = json.load(fp)
        with open(self.cookies_path, 'w') as fp:
            data[self.username] = dict_from_cookiejar(self.session.cookies)
            json.dump(data, fp)


def main():
    v2ex = V2EX(
        username='your username or email',
        password='your password'
    )
    v2ex.cookies_load()
    if not v2ex.has_sign_in():
        v2ex.sign_in()
        v2ex.cookies_save()
    v2ex.get_reward()


if __name__ == '__main__':
    main()
