#!/usr/bin/env python
#-*- coding:utf-8 -*-
##
## 
#  Copyright (C) 
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation.
# 本程序是免费软件，基于GPL许可发布。
# 
# @文件名(file): 115.py
# @作者(author): 龙昌锦(LongChangjin)
# @博客(blog): http://www.xefan.com
# @邮箱(mail): admin@xefan.com
# @QQ: 346202141
# @时间(date): 2012-05-15
# 

# 115网盘自动摇奖程序
# 能够自动登陆并领取空间

import urllib
import urllib2
import cookielib
import json
import re

class Login_115:
    def __init__(self):
        cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(self.opener)
        self.opener.addheaders = [('User-agent', 'IE')]

    def login(self, username, password):
        url = 'https://passport.115.com/?ac=login'
        data = urllib.urlencode({'back':'http://www.115.com', 'goto':'http://115.com', 'login[account]':username, 'login[passwd]':password})
        req = urllib2.Request(url, data)
        try:
            fd = self.opener.open(req)
        except Exception, e:
            print(u'网络连接错误！')
            return False
        fd.close()
        if re.search('error_code', fd.url) != None:
            print(u'%s 密码不正确！\n' % username)
            return False
        print(u'%s 登陆成功，准备摇奖..   ' % username),
        return True

    def yaoyao(self):
        url = 'http://115.com/?ct=index&ac=home'
        req = urllib2.Request(url)
        fd = self.opener.open(req)
        home_page = fd.read()
        codes = re.search('Yao\(\'.*\'', home_page)
        code = codes.group(0)
        if len(code) < 10:
            print(u'今天已经摇过了...')
            return
        fd.close()

        url = 'http://115.com/?ct=ajax_user&ac=pick_space&token=' + code[5:-1]
        req = urllib2.Request(url)
        fd = self.opener.open(req)
        yao_js = json.loads(fd.read())
        fd.close()
        if yao_js['state'] == False:
            print(u'摇奖失败！')
            return
        print(u'\n获取空间：%s, 总空间：%s, 已使用：%s, 获取雨露：%d\n' % 
                (yao_js['picked'], yao_js['total_size'], yao_js['used_percent'], yao_js['exp']))

if __name__ == '__main__':
    l = Login_115()
    name = raw_input("please input username:")
    pswd = raw_input("please input password:")
    if l.login(name, pswd) == False:
        exit(1)
    l.yaoyao()
