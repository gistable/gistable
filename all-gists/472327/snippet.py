#! /usr/bin/python
# -*- coding: utf-8 -*-

import urllib , httplib2 

user="xxxx"
password = "xxxxxxx"

body = {'user':user,'password':password} 
headers = {'Content-type': 'application/x-www-form-urlencoded'}
http = httplib2.Http()
#request0
response, content = http.request('http://10.210.132.20/v5publish/login.php','POST', headers=headers, body=urllib.urlencode(body)) 
print  response['set-cookie']
cookie = response['set-cookie'].split(';')[0]
headers2 = {'Cookie':cookie }

#不要以为取到cookie就万事大吉了，鬼知道服务器还要判断啥!只好老老实实模拟浏览器,一步步走下request1到request3，才能使request4成功得到预期应答
#request1
http.request('http://10.210.132.20/v5publish/index2.php?dep_id=24', 'GET', headers=headers2) 
#request2
http.request('http://10.210.132.20/v5publish/index.php', 'GET', headers=headers2)
#request3
http.request('http://10.210.132.20/v5publish/rollback.php', 'GET', headers=headers2)

header3 = {'Content-type': 'application/x-www-form-urlencoded','Cookie':cookie}
#request4
response,content = http.request('http://10.210.132.20/v5publish/rollback.php', 'POST', headers=headers2,body=urllib.urlencode({'type_select':'133','user_select':'用户选择'}))
print "**************************************************************************"
print response
print "**************************************************************************"
print content
#todo:parse content,get the latest rollback tag

