import re
import subprocess
from urllib2 import urlopen

url = 'http://videolectures.net/ecmlpkdd08_carlson_bief/'

re_flv = re.compile(r'(flv:[\w/]+)')
html = urlopen(url).read()
m = re.search(re_flv, html)
if m:
    flv = m.group(1)
    title = url.split('http://videolectures.net/')[1]
    title = title.replace('/', '')
    p = subprocess.Popen(['rtmpdump', '-r', 'rtmp://oxy.videolectures.net/video',
        '-y', flv, '-a', 'video', '-o', '%s.flv' %title])
    output = p.communicate()[0]
    print output