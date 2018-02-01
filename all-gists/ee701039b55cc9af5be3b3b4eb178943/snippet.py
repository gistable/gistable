#!/usr/bin/env python
# -*- coding: utf-8 -*-

# You can put it into crontab
# * */2 * * * HOME=/home/<your username> DISPLAY=:0 <path to the script>
# it will run every two hours to check for new pictures.

from datetime import datetime
import urllib
import urllib2
import socket

import os
import sys
import re
from subprocess import call

#dir like NationalGeographic/year/month/
today =  datetime.today()
root = os.path.join(os.path.expanduser('~'), 'Pictures/pod')

if not os.path.isdir(root):
    os.makedirs(root)

STOREDIR = root

def setWallPaper(filename):
    call(['fbsetbg', filename])
    # for ubuntu
    # call(['gsettings', 'set', 'org.cinnamon.desktop.background', 'picture-uri', filename])

def getPicture():
    url = "http://cn.bing.com"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0"
    headers = {"User-Agent": user_agent}
    sock = urllib2.urlopen(urllib2.Request(url, None, headers))
    htmlSource = sock.read()
    sock.close()
    img_url = re.findall(r'g_img={url: \"(.*?)\",', htmlSource)[0]
    print img_url

    if re.match(r'^//', img_url):
        download_url = 'http' + img_url
    elif re.match(r'^http', img_url):
        download_url = img_url
    else:
        download_url = 'http://www.bing.com' + img_url

    filename = re.findall(r'([^/]+)', img_url)[-1]
    store_filename = os.path.join(STOREDIR, filename)
    urllib.urlretrieve(download_url, store_filename)
    return store_filename

def setWallpaperOfToday():
    store_filename = getPicture()
    setWallPaper(store_filename)

setWallpaperOfToday()
