'''async_http_client.py

Originally written December 25, 2011 by Josiah Carlson
Released into the public domain.

This simple asynchat.async_chat subclass offers the ability to connect to http
servers to download files. The example download_file() function shows how to
use the class to download files from a remote webserver, automatically
handling redirects and errors.

The updated version from the evening of December 30 now includes support for
HTTPS, chunked transfer encoding, and timeouts. Happy New Year!

This class can be used as a way to fetch remote files for serving, similar to
the requested feature here:
http://code.google.com/p/pyftpdlib/issues/detail?id=197

'''

import asynchat
import asyncore
import httplib
import os
import socket
import ssl
from StringIO import StringIO
import time
import urllib
import urlparse

HEADER = object()
CHUNKED = object()
CHUNK = object()
BODY = object()
PORTS = {'http':80, 'https':443}


class StringBuffer(StringIO):
    # cStringIO can't be subclassed in some Python versions
    def makefile(self, *args, **kwargs):
        return self
    def sendall(self, arg):
        self.write(arg)

class AsyncHTTPRequest(asynchat.async_chat):
    state = HEADER
    response = None
    established = False
    want_read = want_write = True
    def __init__(self, url, data=None, method=None, timeout=30, **kwargs):
        self.last_read = time.time()
        self.timeout = timeout
        self.set_terminator('\r\n\r\n')
        # parse the url and set everything up
        self.url = url
        self.parsed = parsed = urlparse.urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            raise httplib.UnknownProtocol("Can only access http urls")
        self.method = None
        self.established = parsed.scheme == 'http'
        if method and method.upper() in ('GET', 'POST'):
            self.method = method.upper()
        else:
            self.method = 'POST' if data is not None else 'GET'
        self.callbacks = kwargs

        # prepare the http request itself
        post_body = urllib.urlencode(data) if data is not None else None
        host, _, port = parsed.netloc.partition(':')
        http = httplib.HTTPConnection(host)
        http.sock = StringBuffer()
        path = parsed.path
        if parsed.params:
            path += ';' + parsed.params
        if parsed.query:
            path += '?' + parsed.query
        http.request(self.method, path, post_body)

        # connect to the host asynchronously
        asynchat.async_chat.__init__(self)
        self.push(http.sock.getvalue())
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(port, 10) if port else PORTS[parsed.scheme]
        self.connect((host, port))

    def collect_incoming_data(self, data):
        self.last_read = time.time()
        if self.state is HEADER or self.state is CHUNKED or 'body' not in self.callbacks:
            self.incoming.append(data)
        elif (self.state is BODY or self.state is CHUNK) and 'body' in self.callbacks:
            self.callbacks['body'](data)

    def found_terminator(self):
        self.last_read = time.time()
        if self.state is HEADER:
            self.state = BODY
            header_data = StringBuffer(self._get_data().rstrip() + '\r\n\r\n')
            self.response = httplib.HTTPResponse(header_data, method=self.method)
            self.response.begin()
            if 'response' in self.callbacks:
                self.callbacks['response'](self, self.response)
            # error or otherwise...
            if self.response.status != 200:
                self.state = BODY
                return self.found_terminator()
            # chunked transfer encoding: useful for twitter, google, etc.
            if self.response.getheader('Transfer-Encoding', '').lower() == 'chunked':
                self.set_terminator('\r\n')
                self.state = CHUNKED
            else:
                self.set_terminator(self.response.length)

        elif self.state is CHUNKED:
            ch = self._get_data().rstrip().partition(';')[0]
            if not ch:
                # it's probably the spare \r\n between chunks...
                return
            self.set_terminator(int(ch, 16))
            if self.terminator == 0:
                # no more chunks...
                self.state = BODY
                return self.found_terminator()
            self.state = CHUNK

        elif self.state is CHUNK:
            # prepare for the next chunk
            self.set_terminator('\r\n')
            self.state = CHUNKED

        else:
            # body is done being received, close the socket
            self.callbacks.pop('body', None)
            self.terminator = None
            if 'done' in self.callbacks:
                self.callbacks['done'](self)
                self.callbacks.pop('done')
            self.handle_close()

    def handle_close(self):
        if self.parsed.scheme == 'https':
            self.socket = self._socket
        asynchat.async_chat.handle_close(self)
        if 'closed' in self.callbacks:
            self.callbacks['closed'](self)

    # https support
    def readable(self):
        return self.want_read and asynchat.async_chat.readable(self)

    def writable(self):
        if time.time() - self.last_read > self.timeout:
            # should signal timeout here
            self.state = BODY
            self.found_terminator()
            return False
        return self.want_write and asynchat.async_chat.writable(self)

    def _handshake(self):
        try:
            self.socket.do_handshake()
        except ssl.SSLError as err:
            self.want_read = self.want_write = False
            if err.args[0] == ssl.SSL_ERROR_WANT_READ:
                self.want_read = True
            elif err.args[0] == ssl.SSL_ERROR_WANT_WRITE:
                self.want_write = True
            else:
                raise
        else:
            self.want_read = self.want_write = True
            self.established = True

    def handle_write(self):
        if self.established:
            return self.initiate_send()

        self._handshake()

    def handle_read(self):
        if self.established:
            return asynchat.async_chat.handle_read(self)

        self._handshake()

    def handle_connect(self):
        if self.parsed.scheme == 'https':
            self._socket = self.socket
            self.socket = ssl.wrap_socket(self._socket, do_handshake_on_connect=False)

def download_file(url, local_path=None):
    if local_path is None:
        parsed = urlparse.urlparse(url)
        local_path = parsed.path.rpartition('/')[-1]
        if not local_path:
            local_path = 'index.html'
    out = open(local_path, 'wb')
    def redirect(obj, resp, out=out, url=url, local_path=local_path):
        if resp.status in (300, 301, 302, 303, 307):
            print "redirecting", resp.status, url
            download_file(resp.getheader('location'), local_path)
            obj.callbacks['done'] = lambda obj: obj.handle_close()
            obj.callbacks['closed'] = lambda obj: None if out.closed else out.close()
    def done(obj, out=out, url=url):
        print "done downloading", url
        out.close()
        obj.handle_close()
    def close(obj, out=out, local_path=local_path):
        if not out.closed:
            # failed to download
            out.close()
            os.unlink(local_path)
    return AsyncHTTPRequest(url, response=redirect, body=out.write, closed=close, done=done)

def main():
    import sys
    for f in sys.argv[1:]:
        download_file(f)
    asyncore.loop(timeout=.25)

if __name__ == '__main__':
    main()
