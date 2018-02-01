# coding: utf-8
# 更新于2017/10/02，python3测试通过

import re
import requests

# 领取 X 铜币
# 每日登录奖励已领取

base_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.57 Safari/537.36 OPR/40.0.2308.15 (Edition beta)', 'Referer': 'https://www.v2ex.com/signin', 'Origin': 'https://www.v2ex.com'}
base_headers['cookie'] = <你的cookies>

session = requests.Session()
session.headers = base_headers
resp = session.get('https://www.v2ex.com/mission/daily')

if u'每日登录奖励已领取' in resp.text:
    print('Already got it.')
else:
    resp = session.get('https://www.v2ex.com' + re.search(r'/mission/daily/redeem\?once=\d+', resp.text).group())
    print(resp.ok)
