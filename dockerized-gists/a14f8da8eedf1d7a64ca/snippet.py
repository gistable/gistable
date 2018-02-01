#!/usr/bin/env python

import socket
import ssl
import sys
from urlparse import urlparse

'''Crude test client to a HTTP(S) server listening for proxy protocol
connections. Takes a HTTP(S) url as an argument and prints out the raw
response.

$ ppurlcat.py https://localhost/ | head -1
HTTP/1.1 200 OK
'''


class ProxyHTTPRequest:
    def __init__(self, url):
        parsed = urlparse(url)
        dst = parsed.netloc
        if ':' in parsed.netloc:
            dst, dstPort = dst.split(':')
        else:
            dstPort = {'https': 443, 'http': 80}[parsed.scheme]
        self.parsed = parsed
        self.srcPort = 33333
        self.src = '127.0.0.1'
        self.dst = socket.gethostbyname(dst)
        self.dstPort = dstPort

    def proxy_request(self):
        'Generates the proxy protocol string'

        data = map(str, ('PROXY', 'TCP4', self.src, self.dst, self.srcPort,
                         self.dstPort))
        return ' '.join(data) + '\r\n'

    def connect(self):
        '''Creates the TCP connection, sends the proxy protocol string then
           upgrades the socket to SSL if appropriate'''

        self.conn = socket.create_connection((self.dst, self.dstPort))
        self.conn.send(self.proxy_request())
        if self.parsed.scheme == 'https':
            self.conn = ssl.wrap_socket(self.conn)

    def get(self):
        'Sends a simple HTTP request and prints out the raw response'

        self.connect()
        self.conn.send('GET {0} HTTP/1.0\r\n\r\n'.format(self.parsed.path))
        out = ''
        while True:
            lastRead = self.conn.recv()
            if not lastRead:
                break
            else:
                out += lastRead
        return out


if __name__ == '__main__':
    print ProxyHTTPRequest(sys.argv[1]).get()