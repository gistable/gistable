# coding: utf-8

import requests
import re

# Put user name and password here.

v2ex_username = 'v2ex_username'
v2ex_password = 'v2ex_password'
headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.1 Safari/603.1.30',
            'Referer': 'https://www.v2ex.com/signin',
            'Origin': 'https://www.www.v2ex.com'
          }

def v2ex():
    session = requests.Session()
    session.headers.update(headers)

    resp = session.get('https://www.v2ex.com/signin')
    u, p = re.findall(r'class="sl" name="([0-9A-Za-z]{64})"', resp.text)
    once_code = re.search(r'value="(\d+)" name="once"', resp.text).group(1)

    resp = session.post('https://www.v2ex.com/signin', {u: v2ex_username, p: v2ex_password, 'once':once_code, 'next':'/'})
    resp = session.get('https://www.v2ex.com/mission/daily')
    if u'每日登录奖励已领取' in resp.text:
        print('Already done.')
    else:
        resp = session.get('http://v2ex.com' + re.search(r'/mission/daily/redeem\?once=\d+', resp.text).group())
        if resp.ok:
            print('Got it.')

if __name__ == '__main__':
    v2ex()