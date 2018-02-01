# vim: set et sw=4 ts=4 sts=4 fdm=syntax ff=unix fenc=utf8:
#!/usr/bin/python
import json
from subprocess import Popen
import urllib2

_url = 'http://douban.fm/j/mine/playlist?type=n&h=&channel=0'

req = urllib2.urlopen(urllib2.Request(_url))
obj = json.load(req)
playlist = ''
for s in obj['song']:
    playlist = playlist+" "+s['url']

Popen('mpg123 '+playlist, shell=True)