import sys
import urllib2
import subprocess

url = sys.argv[1]
f = urllib2.urlopen(url)
content = f.read()
f.close()

tmp = url.split('/')
tmp1 = ' '.join(map(lambda x: x.capitalize(), tmp[-2].split('-')))
title = tmp[-1].capitalize().split('.')[0] + ' - ' + tmp1 + '.mp3'

print title

num = content.split('http://www.be-at.tv/embed.swf?p=')[1].split('&')[0]

print num

f = urllib2.urlopen('http://www.be-at.tv/CMS/Feeds/Playlist.ashx?page='+num)
content = f.read()
f.close()

uri = "Session" + content.split('url="/Session')[1].split('.flv')[0]

subprocess.call(['rtmpdump', '-r', 'rtmp://media.cdn.be-at.tv:80/cfx/st/',
                '-a', 'cfx/st/', '-y', uri, '-o', '/tmp/audio.flv'])
                
subprocess.call(['ffmpeg', '-i', '/tmp/audio.flv', '-acodec', 'copy', title])
                
