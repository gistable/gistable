from bs4 import BeautifulSoup as bs
from pyquery import PyQuery as pq
from lxml.html import fromstring
import re

import requests

import time

def Timer():
	a = time.time()
	while True:
		c = time.time()
		yield time.time()-a
		a = c

timer = Timer()

url = "http://www.python.org/"
html = requests.get(url).text

num = 100000
print '\n==== Total trials: %s =====' %num

next(timer)

soup = bs(html, 'lxml')
for x in range(num):
	paragraphs = soup.findAll('p')
t = next(timer)
print 'bs4 total time: %.1f' %t

d = pq(html)
for x in range(num):
	paragraphs = d('p')
t = next(timer)
print 'pq total time: %.1f' %t


tree = fromstring(html)
for x in range(num):
	paragraphs = tree.cssselect('p')
t = next(timer)
print 'lxml (cssselect) total time: %.1f' %t


tree = fromstring(html)
for x in range(num):
	paragraphs = tree.xpath('.//p')
t = next(timer)
print 'lxml (xpath) total time: %.1f' %t

for x in range(num):
	paragraphs = re.findall('<[p ]>.*?</p>', html)
t = next(timer)
print 'regex total time: %.1f (doesn\'t find all p)\n' %t
