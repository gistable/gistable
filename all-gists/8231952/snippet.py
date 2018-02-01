#!/usr/bin/env python
from os import system
import sys
import urllib2
import time
import datetime
#from prowlpy import Prowl

def status():
    try:
        response = urllib2.urlopen('http://127.0.0.1:32400/library/sections/1/recentlyAdded',timeout=5)
        return True
    except urllib2.URLError as err: pass
    return False

if not status():
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    #uncomment line 7, 19, and 20 for Prowl support, be sure to input your API key where indicated
    #prowl = Prowl('PROWL_API_KEY_HERE')
    #prowl.post('plex.py', 'PMS Not Responding', 'The Plex Media Server is not responding' + timestamp)

    system('killall "Plex Media Server"')
    time.sleep(5)
    system('open -a "Plex Media Server"')

    system('killall "Plex Home Theater"')
    time.sleep(5)
    system('open -a "Plex Home Theater"')

sys.exit(0)
