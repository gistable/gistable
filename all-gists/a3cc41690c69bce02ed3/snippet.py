#!/usr/bin/env python
# coding=utf8
# author=evi1m0#n0tr00t
# Fri Apr 10 14:14:35 2015

import os
import re
import sys
import wget
import requests
import urlparse
import threadpool as tp

def _archives(author):
    archives_url = 'http://hi.baidu.com/{}/archive'.format(author)
    print '[*] Target URL: {}'.format(archives_url)
    year_content = requests.get(archives_url).content
    years = re.findall('<div class=fi-list id=fiList>(.*?)</section>', year_content)[0]
    months = re.findall('<a href="(.*?)" class="fi-border-bt2', years)
    print '[*] Months count: {}'.format(len(months))
    months_url = []
    archives_list = []
    for month in months:
        if 'month=' in urlparse.urlparse(month).query:
            months_url.append(month)
    for url in months_url:
        month_content = requests.get(url).content
        urls = re.findall('</div><a href="(.*?)" class=info-detail target=_blank>', month_content)
        for u in urls:
            archives_list.append(u)
    return archives_list

def main(url):
    _page = requests.get(url).content
    _title = re.findall('<h2 class="title content-title">(.*?)</h2>', _page)[0]
    _filename = '{author}/{title}'.format(author=sys.argv[1], title=_title)
    print '[+] Download: {}'.format(_title)
    try:
        wget.download(url, out=_filename, bar='')
    except Exception, e:
        print '[-] Error: ' + str(e)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print '[-] Usage: {} Blog_name'.format(sys.argv[0])
        print '[-] Example: {} evi1m0'.format(sys.argv[0])
        sys.exit()
    author = sys.argv[1]
    if not os.path.exists(author):
        os.mkdir(author)
    archives = _archives(author)
    print '[*] Archives statistics: {}'.format(len(archives))
    # threadpool
    pool = tp.ThreadPool(30)
    reqs = tp.makeRequests(main, archives)
    [pool.putRequest(req) for req in reqs]
    pool.wait()
