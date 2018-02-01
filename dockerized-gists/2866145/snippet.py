#! /usr/bin/env python

import SocketServer
import SimpleHTTPServer
import urllib2
from urlparse import urlparse, urljoin

PORT = 8880
FOLLOW_REDIRECT = True
PROXY_RULES = {
    '/habr/' : 'http://habrahabr.ru/',
    '/goo' : 'http://google.com/',
}

class Proxy(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def __do_proxy(self):
        prefix = None
        for key in PROXY_RULES.iterkeys():
            if self.path.startswith(key):
                prefix = key
                break

        if prefix:
            # Strip off the prefix.
            url = urljoin(PROXY_RULES[prefix], self.path.partition(prefix)[2])
            hostname = urlparse(PROXY_RULES[prefix]).netloc

            body = None
            if self.headers.getheader('content-length') is not None:
                content_len = int(self.headers.getheader('content-length'))
                body = self.rfile.read(content_len)

            # set new headers
            new_headers = {}
            for item in self.headers.items():
                new_headers[item[0]] = item[1]
            new_headers['host'] = hostname
            try:
                del new_headers['accept-encoding']
            except KeyError:
                pass

            try:
                self.copyfile(self.__do_request(url, body, new_headers), self.wfile)
            except IOError, e:
                print "ERROR: ", e
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    def __do_request(self, url, body, headers):
        req = urllib2.Request(url, body, headers)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError, e:
            if FOLLOW_REDIRECT and hasattr(e, 'code') and (e.code == 301 or e.code == 302):
                headers['host'] = urlparse(e.url).netloc
                return self.__do_request(e.url, body, headers)
            else:
                response = e
        return response

    def do_GET(self):
        self.__do_proxy()

    def do_POST(self):
        self.__do_proxy()

SocketServer.ThreadingTCPServer.allow_reuse_address = True
httpd = SocketServer.ThreadingTCPServer(('', PORT), Proxy)
print "Starting proxy server at ", PORT
httpd.serve_forever()