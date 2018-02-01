#! /bin/env python
# -*- coding: utf-8 -*-
#
#todo：
#	使用python3
#	计算md5，不用文件名来避免重复，储存 
#	存储信息：json？ pickle？ txt？数据库？ 要包括 点赞数 记录当前状态下一次继续（可行？）
#	改善递归： 循环套递归?
#	py2exe pyinstall？
#	beautiful soup
#	修缮变量名
#	放到树莓派上，通过客户端连接，远程下载（多重方式，email、程序间连接）
#	做个网站把图片放上去………………
#	

import gevent
from gevent import monkey
monkey.patch_all() #debug了  这个要放前面！
from gevent.queue import Queue, Empty, JoinableQueue
import requests
import os
import re
import time

tags = {
	u"Kana+Kurashina",
	u"rina+aizawa",
	u"篠崎愛",
	u"倉科カナ",
	u"新垣結衣",
	u"蒼井優",
	u"逢沢りな",
	u"杉原杏璃",
	u"鈴木愛理"
}

		

re_title = re.compile(r'http://(.*?)\.')
re_img = re.compile(r'data-imageurl="(.*?)">')
re_next = re.compile(r'<a id="next_page_link" href="(.*?)">')
re_name = re.compile(r'.+/(.+)$')
re_tag_host = re.compile(r'http://(.*?)/tagged')
re_tag_title = re.compile(r'http://www.tumblr.com/tagged/(.*)$')

#headers = {"User-Agent": "Mozilla/5.0(Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1),Gecko/20090624 Firefox/3.5"}


re_original_size = re.compile(r'"original_size":{"width":.*?,"url":"(.*?)"}')

re_next_api = re.compile(r'"timestamp":(\d{10})')


api_url = u"http://api.tumblr.com/v2/tagged?tag=%s&api_key=fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4"
def tag_rec(tag,api_url,featured_timestamp):
	#next_url = u"http://api.tumblr.com/v2/tagged?tag=%s&api_key=fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4&before=%s" #% (tag, featured_timestamp)
	next_url = api_url % tag
	if not featured_timestamp == 0:
		next_url = next_url + "&before=" + featured_timestamp
		print next_url
	r = requests.get(next_url)
	c = r.content
	imgs_url = re.findall(re_original_size, c)
	imgs = {}
	imgs[tag] = list(imgs_url)
	#print imgs
	#tasks.put_nowait(imgs) #不阻塞
	tasks.put(imgs) #阻塞
	#print c
	print re.findall(re_next_api, c)
	featured_timestamp = re.findall(re_next_api, c)[-1]
	next_url  = api_url + "&before=" + featured_timestamp
	return tag_rec(tag,api_url,featured_timestamp) , tag, api_url, featured_timestamp #这里优化递归？计个数，然后传递到下一个递归

def tr(tag):
	api_url = u"http://api.tumblr.com/v2/tagged?tag=%s&api_key=fuiKNFp9vQFvjLNvx4sUwti4Yb5yGutBN4Xh10LXZhhRKjWlV4"
	featured_timestamp = 0
	return tag_rec(tag,api_url,featured_timestamp)



def worker(n):
	while True:
		imgs = tasks.get()
		title = [i for i in imgs][0]
		if not os.path.exists(title):
			os.makedirs(title)

		for i in imgs:
			
			for img in imgs[i]:   
				#print img
				img = img.replace('\\','')  #http:\/\/25.media.tumblr.com\/14c3326546cfb75756649dbf7f7dd4a1\/tumblr_murtrykPmS1rpq0i8o1_1280.jpg
				# 去除\反斜杠
				filename = re.findall(re_name, img)[0]  #filename				
				
				if filename in FILEEXISTS:
					print title,filename, 'exists'
					continue
				
				
				name = os.path.join(title, filename )
				gevent.sleep(0) #sleep 在循环内快? 这里快！ 400k
				if not os.path.exists(name) :
					r = requests.get(img) #1
					c = r.content #计算md5！！！
					print 'worker %d get one at ' % n ,title
					with open(name,'wb') as f:
						f.write(c)
						FILEEXISTS.append(filename)
					
				else:
					print name , 'exists'

def filewalk(path):
	#return ['file', ... ]
	w = os.walk(path)
	files = []
	[files.append(x) for i in w for x in i[2]]  #不能是for x in i for i in w 这个反回一堆None
	#for i in w:
	#	for x in i[2]:
	#		files.append(x)
	return files

START = time.time()
FILEEXISTS = filewalk('./')
while True:
	tasks = JoinableQueue(maxsize = 10)  #debug了
	#tasks = Queue()
	tasks.join()
	
	#tag = u"rina+aizawa"  #tag
	recs = [ gevent.spawn(tr, tag) for tag in tags]
	
	
	workers = [ gevent.spawn(worker, n) for n in xrange(20) ]  
	
	gevent.joinall( workers )
	gevent.joinall( recs )
	