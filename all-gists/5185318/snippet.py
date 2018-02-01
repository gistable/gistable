#!/usr/bin/env python
# -*- coding: UTF-8 -*-
##meizi.py
##python meizi.py <pic|ooxx> <page_from> <page_to> <output_file>
from bs4 import BeautifulSoup
from urllib2 import urlopen
import sys
f = open(sys.argv[4],'w')
for i in range(int(sys.argv[2]), int(sys.argv[3]) + 1):
    content = urlopen('http://jandan.net/%s/page-%d#comments' % sys.argv[1], i).read()
    soup = BeautifulSoup(content)
    for i in soup.find_all('li'):
        for j in i.find_all('p'):
            for k in j.find_all('img'):
                try:
                    f.write("%s\n" % k.get('src'))
                except:
                    continue
f.close()
