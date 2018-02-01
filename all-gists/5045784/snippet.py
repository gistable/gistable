# coding: utf-8
from __future__ import unicode_literals
import re
import sys
import requests
import HTMLParser

cookie_t = ''
uid      = ''
filename = ''
pages    = 1
baseurl  = 'http://status.renren.com/GetSomeomeDoingList.do?userId=%s&curpage=%d'

# html preprocessing
p1 = re.compile(r'<a[^>]+>')
p2 = re.compile(r'</a>')
p3 = re.compile(r"<img.*alt='(.*)'.*/>")
hp = HTMLParser.HTMLParser()
p  = lambda s: hp.unescape(p3.sub(r'[\1]', p1.sub('[', p2.sub(']', s)))).encode('utf-8')

# output
sys.stdout = open(filename, 'w')

for i in xrange(pages):
    # fetching
    sts = requests.get(baseurl % (uid, i), cookies={'t': cookie_t}).json()

    for st in sts['doingArray']:
        print st['dtime']
        print p(st['content'])
        if 'rootContent' in st:
            print p(st['rootContent'])
        print