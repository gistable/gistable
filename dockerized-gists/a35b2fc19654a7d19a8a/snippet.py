# -*- coding: utf-8 -*-


from urllib import urlretrieve
from urllib2 import urlopen
import re

page = urlopen('http://192.168.0.10/DCIM').read()
#print page
m = re.findall('(wlansd.*DCIM.*;)',page)

for entry in m:
    folder = entry.split(',')[1]
    #print folder

    page = urlopen('http://192.168.0.10/DCIM/'+folder).read()
    #print page
    sub = re.findall('wlansd.*DCIM.*;',page)

    for f in sub:
        img = f.split(',')[1]
        url = 'http://192.168.0.10/DCIM/' + folder + '/' + img
        print 'Retrieving ' + url
        urlretrieve(url,img)