#!/usr/bin/env python
#coding:utf-8

import os,time,socket
import urllib,re

urlList = ['http://jandan.net/ooxx/page-%d' % i for i in range(1, 911)]

globnum = 1

def get_html(url):
    page = urllib.urlopen(url)
    time.sleep(0.5)
    html = page.read()
    return html

def get_img(html):
    global globnum
    # reg = r'src="(.*?\.jpg)" />'
    reg = r'src="(.*?\.jpg)"[\s]*/>'
    imgre = re.compile(reg)
    imglist = re.findall(imgre, html)
    for imgurl in imglist:
        try:
            urllib.urlretrieve(imgurl, '%s.jpg'%globnum)
            time.sleep(3)
        except IOError:
            time.sleep(0.5)
        except:
            print 'time out'
        globnum+=1

# html = get_html('http://jandan.net/ooxx/page-1')

socket.setdefaulttimeout(30)

for i in urlList:
    html = get_html(i)
    print get_img(html)
    time.sleep(1)
