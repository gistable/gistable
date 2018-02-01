#!/usr/bin/env python
# -*- coding:utf-8 -*-
# extract YouTube videoids from html

import re
import json
import urllib2
from BeautifulSoup import BeautifulSoup

def get_videoids(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    title = soup('title')[0].string
    videoids = []
    for element in soup('embed'):
        src = element.get('src')
        if re.search('v\/([-\w]+)', src):
            videoids.append(re.search('v\/([-\w]+)', src).group(1))
    for element in soup('iframe'):
        src = element.get('src')
        if re.search('youtube.com\/embed\/', src):
            videoids.append(re.search('embed\/([-\w]+)', src).group(1))
    for element in soup('iframe'):
        src = element.get('src')
        if re.search('youtube.com\/embed\/', src):
            videoids.append(re.search('embed\/([-\w]+)', src).group(1))
    for element in soup('a'):
        href = element.get('href')
        if href and re.search('youtube.com\/watch\?v=([-\w]+)', href):
            videoids.append(re.search('youtube.com\/watch\?v=([-\w]+)', href).group(1))
        if href and re.search('youtu\.be\/([-\w]+)', href):
            videoids.append(re.search('youtu\.be\/([-\w]+)', href).group(1))

    res = {}
    res['title'] = title
    res['videoids'] = list(set(videoids))
    return res

if __name__ == '__main__':
    print json.dumps(get_videoids('http://blog.livedoor.jp/darkm/archives/51472120.html'))
