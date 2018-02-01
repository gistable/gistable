#! /usr/bin/env python2
# -*- coding: utf-8 -*-
from weibo import APIClient
import urllib
import requests 

# 个人信息
__author__  = 'GentlemanMod'
__email__   = 'GentlemanMod@gmail.com'
__version__ = 'v1'

# 开启调试输出(0 or 1)
debug = 0

# 构造headers信息
user_agent = (
  'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '
  'Chrome/20.0.1132.57 Safari/536.11'
)
session = requests.session()
session.headers['User-Agent'] = user_agent
session.headers['Host'] = 'api.weibo.com'

# 设置全局变量
global api_key, api_secret, callback_url, userid, password
api_key = '3495549134'
api_secret = '514f3edcb22f31f58cf71144174d5d5f'
callback_url = 'http://gentlemanmod.cnblos.com'
userid = 'xxxxxx@xxxxx.com'
password = 'xxxxxxxxxxxxx'

# 初始化API client
global client, referer_url
client =  APIClient(app_key=api_key, app_secret=api_secret, redirect_uri=callback_url)
referer_url = client.get_authorize_url()
if debug: print 'referer_url: %s' % referer_url

# 获取回调地址的code
def get_code():
  # 构造post数据
  data = {
    'client_id': api_key,
    'redirect_uri': callback_url,
    'userId': userid,
    'passwd': password,
    'isLoginSina': '0',
    'action': 'submit',
    'response_type': 'code'
  }

  session.headers['Referer'] = referer_url

  # post数据到渣浪服务器
  resp = session.post(
    url = 'https://api.weibo.com/oauth2/authorize',
    data = data
  )
  
  if debug: print 'get url: %s' % resp.url
  if debug: print 'code is: %s' % resp.url[-32:]
  
  # 截取回调url中的code
  code = resp.url[-32:]
  return code


# 发文字微博
def weibo_text(text):
  # post构造的数据获取code
  code = get_code()

  # 获取渣浪授权令牌和期限
  token = client.request_access_token(code)
  client.set_access_token(token.access_token, token.expires_in)

  # 发微博
  client.statuses.update.post(status=text)

# 发图片微博
def weibo_pic(text, picture):
  # post构造的数据获取code
  code = get_code()

  # 获取渣浪授权令牌的期限
  token = client.request_access_token(code)
  client.set_access_token(token.access_token, token.expires_in)

  # 发图片微博
  Pic = open(picture, 'rb')
  client.statuses.upload.post(status=text, pic=Pic)
  Pic.close()

if __name__ == '__main__':
  weibo_text('测试发布文字微博')
  weibo_pic('测试发布图片微博', '/home/michellgaby/img/mugi.jpg')