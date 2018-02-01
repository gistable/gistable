# -*- coding:utf-8 -*-
import re
import urllib2
from lib.BeautifulSoup import BeautifulSoup

agent="""Sosospider+(+http://help.soso.com/webspider.htm)"""

blog_url = 'http://blog.sina.com.cn/s/articlelist_1517582220_0_1.html'
spider_handle = urllib2.urlopen(blog_url)
blog_content = spider_handle.read()
soup = BeautifulSoup(blog_content, fromEncoding='utf-8')
item_list = soup.findAll('span', {'class':'atc_title'})

urls = ['http://blog.csdn.net/heiyeshuwu/archive/2010/12/19/6085876.aspx']
#for item in item_list:
#    urls.append(item.a['href'])
    
for url in urls:
    request = urllib2.Request(url)
    request.add_header('User-Agent', agent)
    handle = urllib2.urlopen(request).read()
    article_soup = BeautifulSoup(handle, fromEncoding='utf-8')
    title = article_soup.find('h1',{'class':'title_txt'})
    content = article_soup.find('div',{'id':'sina_keyword_ad_area2'})
#    tmp = []
#    for c  in content.contents:
#        print type(c)
#        tmp.append(c.__str__('utf-8'))
    print url
    print title.contents
    print title.contents[2].replace('\t', '').replace('\r\n', '')
#    print ''.join(tmp)
    exit()
    