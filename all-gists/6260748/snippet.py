#coding=utf-8

##版本：1.0
##环境：python2.7
##作者：moxie
##日期：2013.08.18
##第三方依赖：requests和BeautifulSoup4

import re
import requests as rq
from bs4 import BeautifulSoup as bs
import shutil
import os

#全局变量
lgurl = 'http://mlook.mobi/member/login'
prefix = 'http://mlook.mobi/?order=updatetime&page='
host = 'http://mlook.mobi'

s = os.sep    #根据unix或win，s为\或/
root = "d:" + s + "mlook" + s

hds = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36',
		'Referer':'http://mlook.mobi/member/login',
		}

#使用会话保持登录
s = rq.Session()

#用bs获取formhash
login_page = s.get(lgurl).content
soup = bs(login_page)
formhash = soup.find_all('input', {'type': 'hidden', 'name': 'formhash'})[0]['value']

#表单数据
pstdata = {
    'formhash':formhash,
	'person[login]':'76398711@qq.com',
	'person[password]':'123456',
	}

#登录
r = s.post(url = lgurl,data = pstdata, headers = hds)
print 'logined'
#寻找该页所有电子书的url
def bookurl(pageurl):
	page = s.post(pageurl,headers = hds)
	pat = r'<div.*?<h3>.*?href="(.*?)"'
	pattern = re.compile(pat,re.S)
	urlends = pattern.findall(page.content)
	bookurls = []
	for urlend in urlends:
		bookurls.append(host + urlend)
	print 'bookurl done'
	return bookurls
#在电子书页面寻找下载链接并下载
def dlurl(bookurl):
	bkpage = s.post(bookurl,headers = hds)
	pattitle = re.compile(r'<title>(.*?) mLook',re.S)
	patdlurl = re.compile(r'<a class="download" href="(.*?)".*?格式：(.*?)"',re.S)
	bkpcontent = bkpage.content
	title = pattitle.findall(bkpcontent)[0].decode('utf-8')
	dls = patdlurl.findall(bkpcontent)
	for dl in dls:
		durl = host + dl[0]
		fname = title.rstrip() + '.' + dl[1]
		abspath = os.path.join(root,fname)
		if False == os.path.exists(root):#判断文件夹是否存在，不存在则创建
			os.mkdir(root)
		if dl[1] in ['epub','mobi'] and False == os.path.exists(abspath):#只下载epub和mobi格式的文件，已经下载过则忽略
			print 'get bookurl'
			bookcont = s.get(durl,stream = True,headers = hds)
			print 'downloading %s...' % fname
			with open(abspath,'wb') as ebook:
				shutil.copyfileobj(bookcont.raw,ebook)
				print '%s downloaded!' % fname
			del bookcont


if __name__ == '__main__':
	try:
		num = int(raw_input('Please input the number of pages you want to download into D:mlook\n'))
		pg = 1
		while 1 <= pg <= num:
			for bkurl in bookurl(prefix + str(pg)):
				dlurl(bkurl)
			pg += 1
	except:
		print 'input again'
