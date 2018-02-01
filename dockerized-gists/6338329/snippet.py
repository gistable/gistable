#! /usr/bin/env python
'''
ymrip
Minimal web interface to download video and audio from YouTube

Dependencies:
    - pytube (https://github.com/NFicano/pytube)
    - ffmpeg
'''

__author__ = 'Julian Melchert <jpm124@uclive.ac.nz>'
__version__ = '0.0.4'

from os import O_NONBLOCK
import sys
from urlparse import parse_qs
from urllib import unquote
import socket
import subprocess
from threading import Thread
from fcntl import fcntl, F_SETFL
from select import select
from time import sleep

from pytube import YouTube

class MusicRipper(Thread):

    def __init__(self, c, url):
        self.sock = c
        self.url = url
        Thread.__init__(self)

    def onData(self, data):
        # write
        self.sp.stdin.write(data)
        # read/write
        try:
            self.sock.send(self.sp.stdout.read())
        except IOError:
            pass

    def onProgress(self, d, t):
        sys.stdout.flush()
        sys.stdout.write('\r %.2f %%' % (d * 100.0 / t))

    def run(self):
        try:
            self.do()
        except:
            pass
        
        self.sock.close()

    def do(self):
        y = YouTube()
        y.url = self.url
        v = max(y.filter('mp4'))
        self.sp = subprocess.Popen( ('ffmpeg', '-i', '-', '-vn', '-acodec', 'copy', '-f', 'adts', '-'),
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        fcntl(self.sp.stdout.fileno(), F_SETFL, O_NONBLOCK)
        m  = u'HTTP/1.1 200 OK\r\n'
        m += u'Content-Type: audio/mpeg\r\n'
        m += u'Content-Disposition: attachment; filename="%s.adts"\r\n' % v.filename
        self.sock.send(m.encode('utf-8') + '\r\n')
        v.download(on_data=self.onData, chunk_size=2**11)
        fcntl(self.sp.stdout.fileno(), F_SETFL, O_NONBLOCK ^ 0b111111111111)
        self.sp.stdin.close()
        self.sp.wait()
        data = self.sp.stdout.read()
        while data:
            print data.__repr__()
            self.sock.send(data)
            data = self.sp.stdout.read()

class VideoRipper(Thread):

    def __init__(self, c, url):
        self.sock = c
        self.url = url
        Thread.__init__(self)

    def onData(self, data):
        self.sock.send(data)

    def run(self):
        try:
            self.do()
        except:
            pass
        self.sock.close()

    def do(self):
        y = YouTube()
        y.url = self.url
        v = max(y.filter('mp4'))
        m  = u'HTTP/1.1 200 OK\r\n'
        m += u'Content-Type: video/mp4\r\n'
        m += u'Content-Disposition: attachment; filename="%s.mp4"\r\n' % v.filename
        self.sock.send(m.encode('utf-8') + '\r\n')
        v.download(on_data=self.onData, chunk_size=2**11)

class Server(object):

    html = u''.join(('<html><head><title>.:[ymrip]:.</title>',
        '<style type="text/css">body{color:white;text-align:center;',
        'background-image:url(http://i.imgur.com/Kz3nMGF.jpg);}</style>',
        '</head><body><br /><br />%s<br /><form name="input" action="get" ',
        'method="get" style="text-align: center;"><table><td><tr><input t',
        'ype="text" name="url" size="42"/></tr><tr><input type="checkbox" ',
        'name="mode" value="music"></tr><tr><input type="submit" value="Dow',
        'nload"/></tr></td></table></form></body></html>')).encode('utf-8')

    def __init__(self, host='127.0.0.1', port=8787):
        self.host = host
        self.port = port

    def _processRequest(self, c):
        data = c.recv(512)
        print data.__repr__()
        if data.startswith('GET / HTTP/1.1'):
            m  = 'HTTP/1.1 200 OK\r\n'
            m += 'Content-Type: text/html; charset=utf-8\r\n'
            m += 'Content-Length: %d\r\n' % len(self.html) 
            c.send(m + '\r\n')
            c.send(self.html % '')
            sleep(0.05)
            c.close()
        elif data.startswith('GET /get?'):
            params = data.partition(' HTTP/1.1\r\n')[0].rpartition('GET /get?')[2]
            params = parse_qs(params)
            url = unquote(params['url'][0])
            if 'mode' in params and 'music' in params['mode']:
                t = MusicRipper(c, url)
                t.start()
            else:
                t = VideoRipper(c, url)
                t.start()

    def run(self):
        s = socket.socket()
        s.bind((self.host, self.port))
        s.listen(5)

        l = [s]
        n = []

        self.alive = True
        while self.alive:
            r, w, e = select(l, n, n, 0.5)
            if r:
                try:
                    c, d = s.accept()
                    self._processRequest(c)
                except:
                    print sys.exc_info()
                    try:
                        c.close()
                    except:
                        pass

        s.close()

    def kill(self):
        self.alive = False


if __name__ == '__main__':

    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        server.kill()
