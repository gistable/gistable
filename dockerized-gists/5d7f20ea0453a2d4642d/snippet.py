# http://bangumi.tv/anime/browser/tv/?sort=rank&page=57
#!/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib2
from bs4 import BeautifulSoup

headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
url_base = 'http://bangumi.tv/anime/browser/tv/?sort=rank&page='
page_num_total = 57
#per_page_item_num = 24
outfile = open('anime_id.txt','w')

if __name__=="__main__":
	for page_num in range(1,page_num_total + 1):
		print page_num
		url = url_base + str(page_num)
		req = urllib2.Request(url, headers = headers)
		html_doc = urllib2.urlopen(req).read()
		soup = BeautifulSoup(html_doc, 'lxml')
		lines = soup.find(id="browserItemList").find_all('li')
		for l in lines:
			outfile.write(l.a["href"] + '\n')
	outfile.close()