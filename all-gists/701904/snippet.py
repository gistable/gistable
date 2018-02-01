"""
Simple backend for nginx memcached module
Written by Wojtek 'suda' Siudzinski <admin@suda.pl>
Gist: https://gist.github.com/701904

Nginx config:

    location /static {
            add_header              X-Origin                Memcached;
            expires                 modified +48h;
            set                     $memcached_key  $uri;
            memcached_pass          127.0.0.1:11211;
            error_page 404 = @static;
    }
    
    location @static {
            add_header              X-Origin                Disk;
            proxy_set_header        X-Memcached-Path        /var/www/example.com;
            proxy_set_header        X-Memcached-Key         $uri;
            proxy_set_header        X-Memcached-Expires     86400;
            proxy_pass              http://localhost:9876;
    }

Check "X-Origin" header to see where your static files came from
"""

import memcache, urllib, os
import SocketServer, SimpleHTTPServer
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

PORT = 9876
DEBUG = False
MEMCACHED = ['127.0.0.1:11211']

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        if None != self.headers['X-Memcached-Path']:
            path = self.headers['X-Memcached-Path']+self.path
            
            if os.path.isfile(path):
                try:
                    self.copyfile(urllib.urlopen(path), self.wfile)
                except IOError:
                    if DEBUG:
                        print "Error: cannot write stream"
                f = open(path, 'rb')
                mc.set(self.headers['X-Memcached-Key'], f.read(), int(self.headers['X-Memcached-Expires']))
                f.close()
                if DEBUG:
                    print path+" stored for "+self.headers['X-Memcached-Expires']+"s"
            else:
                if DEBUG:
                    print path+" not found or is a directory"
    
    def finish(self):
        try:
            SimpleHTTPServer.SimpleHTTPRequestHandler.finish(self)
        except IOError, e:
            if e.errno != 32 and DEBUG:
                print 'Error: broken pipe'

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':            
    mc = memcache.Client(MEMCACHED, debug=0)
    httpd = ThreadedHTTPServer(('', PORT), Proxy)
    httpd.daemon_threads = True
    httpd.allow_reuse_address = 1
    if DEBUG:
        print "Serving at port", PORT
    httpd.serve_forever()