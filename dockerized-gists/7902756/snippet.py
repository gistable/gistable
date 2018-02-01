# coding: UTF-8

import sys
import urllib2

def expandURL(shortURL):
    url = urllib2.urlopen(shortURL).geturl()
    return url