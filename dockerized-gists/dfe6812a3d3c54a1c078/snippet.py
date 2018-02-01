#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: zhibin
# @Date:   2015-03-18 18:20:21
# @Last Modified by:   zhibin
# @Last Modified time: 2015-03-18 18:25:03



from urllib import urlencode
import cookielib, urllib2,urllib
def __login():
	headers={'User-Agent':'Mozilla/5.0 (Windows;U;Windows NT 5.1;zh-CN;rv:1.9.2.9)Gecko/20100824 Firefox/3.6.9'}
	values = {'form_email':'****','form_password':'******','remember':1,'source':'simple','redir':'http://www.douban.com'}
	loginUrl = 'http://www.douban.com/accounts/login'
	data = urllib.urlencode(values)
	cookiejar = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
	urllib2.install_opener(opener)
	request = urllib2.Request(loginUrl ,data ,headers)
	result = urllib2.urlopen(request)
	login_result = result.read()
	if(login_result.find('.com/accounts/logout')):
		print 'login success'
	else :
		print 'login faild'

if __name__=='__main__':
	__login()