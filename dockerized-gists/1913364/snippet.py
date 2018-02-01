#!/usr/bin/env python
#coding:utf-8

import os, sys
import json
import requests
from urllib import urlencode

Client_ID = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.apps.googleusercontent.com"
Client_secret = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
base_url = "https://accounts.google.com/o/oauth2"

####
def get_req_token():
  req_token_param = {
      'response_type':"code",
      'client_id':Client_ID,
      'redirect_uri':"urn:ietf:wg:oauth:2.0:oob",
      'scope':"https://www.googleapis.com/auth/userinfo.profile \
             https://www.googleapis.com/auth/userinfo.email",
      }

  req_url = base_url+'/auth?%s'%(urlencode(req_token_param))
  r = requests.get(req_url, allow_redirects=True)
  print req_url
  if r.status_code == 200:
    open_chrome(req_url)
  else:
    print 'get fail'

###
def open_chrome(req_url):
  if sys.platform == 'darwin':
    os.popen('open /Applications/Google\ Chrome.app "%s"'%(req_url))
  else:
    pass

###
def input_auth_code():
  authorization_code = raw_input('\n\nWhat your auth code>>> \t')
  return authorization_code

###
def make_token_param(auth_code):
  global Client_ID, Client_secret
  data_hash = {
      'code'          : auth_code,
      'client_id'     : Client_ID,
      'client_secret' : Client_secret,
      'redirect_uri'  : "urn:ietf:wg:oauth:2.0:oob",
      'grant_type'    : "authorization_code"
      }
  content_length = len(urlencode(data_hash))
  data_hash['content-length'] = str( content_length )
  return data_hash

###
def get_token_code(auth_code):
  r = requests.post(
                   url=base_url + '/token',
                   data=urlencode(make_token_param(auth_code))
                   )
  res_token = json.loads(r.text)
  print '\nYour token is', res_token['access_token']
  return res_token['access_token']

def get_user_info(acc_token):
  req_url = "https://www.googleapis.com/oauth2/v2/userinfo"
  headers = {'Authorization': 'OAuth ' + acc_token}
  r = requests.get(req_url, headers=headers)
  ret = json.loads(r.text)
  print '\nYour user infomation:\n'
  for i in ret:
    print i, '\t\t', ret[i]

if __name__ == '__main__':
  print '=' * 80
  # リクエストトークンを取得する＞クローム経由
  get_req_token()
  # 入力待ち
  key = input_auth_code()
  # アクセストークン取得
  token = get_token_code(key)
  # ユーザー情報取得
  get_user_info(token)
