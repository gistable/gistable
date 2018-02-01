#!/usr/bin/env python
# coding=utf-8

import codecs
from lxml.html.soupparser import fromstring
from lxml.cssselect import CSSSelector
import re
import requests


DEBUG = False

index_url = 'learn-duolingo-english-to-turkish/lessons'
base_url = 'https://elon.io/'

start_url = base_url + index_url
selector_list = CSSSelector("div.list-group")

fh = codecs.open("elon-io-duolingo-turkish.csv", 'w', 'UTF-8')

if DEBUG:
    print "GET %s" % start_url
response = requests.get(start_url)
root = fromstring(response.content)
lessons = selector_list(root)[0]

counter = 0
for lesson in lessons.findall('a')[1:]:  # Skip first (empty)
    href = lesson.attrib['href']
    pageurl = base_url + href
    tag = re.sub('.*\/', '', href)
    if DEBUG:
        print "GET %s" % pageurl
    response = requests.get(pageurl)
    pageroot = fromstring(response.content)
    selector_rows = CSSSelector("tbody tr")
    rows = selector_rows(pageroot)
    for row in rows:
        cells = row.findall('td')
        english = cells[0].text
        turkish = cells[1].find('a').text
        if DEBUG:
            print repr(turkish), english
        # Fix funky encodings
        tmp = turkish
        tmp = tmp.replace(u"\xc4\x9f", u"\u011f") # ǧ
        tmp = tmp.replace(u"\xc4\u0105", u"\u0131") # ı
        tmp = tmp.replace(u"\u0139\x9f", u"\u015f") # ş
        tmp = tmp.replace(u"\u0102\xa7", u"\u00e7") # ç
        tmp = tmp.replace(u"\u0102\u015b", u"\u00f6") # ö
        tmp = tmp.replace(u"\u0102\u017a", u"\u00fc") # ü
        tmp = tmp.replace(u"\u0e23\u0e07", u"\u00e7") # ç
        if tmp != turkish:
            print "Changed %s to %s in %s" % (turkish, tmp, tag)
            turkish = tmp
        fh.write("%s\t%s\t%s\n" % (english, turkish, tag))
    counter += 1

fh.close()
