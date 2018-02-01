#!/usr/bin/env python
#-*- coding:utf-8 -*-

__author__ = 'bluele'
__version__ = '0.10'
__license__ = 'MIT'

__doc__ = """
# simple running
$ hserve
Serving at xxx.xxx.xxx.xxx:8000
Directory path is /path/to/current/directory
Press Ctr^c to stop.

# change document root
$ hserve -p 8080 -d ~/
Serving at xxx.xxx.xxx.xxx:8080
Directory path is /path/to/home/directory
Press Ctr^c to stop.

# run as cgi-server
$ hserve -c
Running by CGI HTTP Server mode.
Serving at xxx.xxx.xxx.xxx:8000
Directory path is /path/to/current/directory
Press Ctr^c to stop.

# set basic authentication to server.
$ hserve -b username=password
Set basic authentication to server.
Serving at xxx.xxx.xxx.xxx:8000
Directory path is /path/to/current/directory
Press Ctr^c to stop.

In case running http-server by cgi-mode,
you need to put cgi-script under 'cgi-bin/' directory.
"""

from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from CGIHTTPServer import CGIHTTPRequestHandler
from SocketServer import ThreadingMixIn


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


class BasicAuthMixin(object):
    _basic_auth_key = None
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Please enter username and password."')
        self.send_header('Content-type', 'text/html')
        self.end_headers()


class SimpleBasicAuthHandler(SimpleHTTPRequestHandler, BasicAuthMixin):
    """ Main class to present webpages and authentication. """

    def do_GET(self):
        """ Present frontpage with user authentication. """
        if self.headers.getheader('Authorization') == None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
        elif self.headers.getheader('Authorization') == self._basic_auth_key:
            SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write('Not authenticated')


class CGIBasicAuthHandler(CGIHTTPRequestHandler, BasicAuthMixin):
    """ Main class to present webpages and authentication. """

    def do_GET(self):
        """ Present frontpage with user authentication. """
        if self.headers.getheader('Authorization') == None:
            self.do_AUTHHEAD()
            self.wfile.write('no auth header received')
        elif self.headers.getheader('Authorization') == self._basic_auth_key:
            CGIHTTPRequestHandler.do_GET(self)
        else:
            self.do_AUTHHEAD()
            self.wfile.write('Not authenticated')


def get_ip_address():
    import socket
    return socket.gethostbyname(socket.gethostname())


def get_parser():
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-p', '--port',
                      dest='port',
                      default=8000,
                      help='bind socket to port number.')
    parser.add_option('-d', '--directory',
                      dest='directory',
                      default='.',
                      help='serve directory path.')
    parser.add_option('-c', '--cgi',
                      dest='cgi',
                      default=False,
                      action='store_true',
                      help='Is running by CGI mode.')
    parser.add_option('-b', '--basicauth',
                      dest='basicauth',
                      help='Username and Password for basic auth.')
    return parser


def get_simple_http_server(port, is_basicauth=False, **kwargs):
    if is_basicauth:
        print u'Set basic authentication to server.'
        handler = SimpleBasicAuthHandler
        handler._basic_auth_key = get_authorization_key(kwargs['username'], kwargs['password'])
    else:
        handler = SimpleHTTPRequestHandler
    return ThreadingHTTPServer(('', port), handler)


def get_cgi_http_server(port, is_basicauth=False, **kwargs):
    if is_basicauth:
        print u'Set basic authentication to server.'
        handler = CGIBasicAuthHandler
        handler._basic_auth_key = get_authorization_key(kwargs['username'], kwargs['password'])
    else:
        handler = CGIHTTPRequestHandler
    return ThreadingHTTPServer(('', port), handler)


def get_authorization_key(username, password):
    import base64
    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    return 'Basic %s' % base64string


def parse_basic_auth_pair(string):
    if string is None:
        return dict()
    username, password = string.split('=')
    return dict(username=username, password=password)


def main():
    from os.path import normpath, abspath, isdir
    from os import chdir
    import sys

    (options, args) = get_parser().parse_args()
    port = int(options.port)
    directory = normpath(abspath(options.directory))
    ip_address = get_ip_address()
    is_basic_auth = options.basicauth != None

    if not isdir(directory):
        print u'"%s" is not directory.' % directory
        sys.exit(1)

    chdir(directory)

    if options.cgi == True:
        print u'Running by CGI mode.'
        httpd = get_cgi_http_server(port, is_basic_auth, **parse_basic_auth_pair(options.basicauth))
    else:
        httpd = get_simple_http_server(port, is_basic_auth, **parse_basic_auth_pair(options.basicauth))

    print u'Serving at %s:%s' % (ip_address, port)
    print u'Document root: %s' % directory
    print u'Press Ctr^c to stop.\n'
    httpd.serve_forever()


if __name__ == '__main__':
    main()