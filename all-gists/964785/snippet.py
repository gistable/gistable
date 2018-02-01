# -*- Encoding: utf-8 -*-
import urllib
from httplib2 import Http


LOGIN_URL = 'http://www.renren.com/PLogin.do'
FRIENDS_URL = 'http://friend.renren.com/myfriendlistx.do'

h = Http()
h.follow_redirects = False

login_data = {
    'email': 'MMMMMM@EXAMPLE.COM',
    'password': 'ZZZZZZ',
    'origURL': 'http://www.renren.com/home',
    'domain': 'renren.com',
}

headers_template = {
    'Accept': 'application/xml,application/xhtml+xml,text/html;q=0.9,text/plain;q=0.8,image/png,*/*;q=0.5',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'www.renren.com',
    'Referer': 'http://www.renren.com/Home.do',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.65 Safari/534.24',
}

headers = headers_template.copy()
headers['Content-type'] = 'application/x-www-form-urlencoded'
resp, content = h.request(LOGIN_URL, 'POST', headers=headers,
                          body=urllib.urlencode(login_data))

if resp['status'] == '302':
    headers = headers_template.copy()
    headers['Cookie'] = resp['set-cookie']
    resp, content = h.request(resp['location'], headers=headers)

headers = headers_template.copy()
headers['Host'] = 'friend.renren.com'
headers['Cookie'] = resp['set-cookie']

resp, content = h.request(FRIENDS_URL, headers=headers)
print content
