#!/usr/bin/env python2
import urllib2
import lxml.html
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
if len(sys.argv) < 2:
    sys.exit("URL not found")

url = sys.argv[1]
html_page = urllib2.urlopen(url=url)
dom = lxml.html.fromstring(html_page.read())
for link in dom.xpath('//a/@href'):
    print str(link).encode('utf-8', 'ignore')