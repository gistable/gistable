"""
Provide HTTP proxy support for Python's xmlrpclib, via urllib2.

For example:
    >>> transport = HTTPProxyTransport({
    ...     'http': 'http://myproxyserver',
    ... })
    
    >>> server = xmlrpclib.Server('http://blogsearch.google.com/ping/RPC2',
    ...                           transport=transport)
    >>> print server.weblogUpdates.ping(
    ...     'Official Google Blog',
    ...     'http://googleblog.blogspot.com/',
    ...     'http://googleblog.blogspot.com/'
    ... )
"""


import urllib2
import xmlrpclib


class Urllib2Transport(xmlrpclib.Transport):
    def __init__(self, opener=None, https=False, use_datetime=0):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self.opener = opener or urllib2.build_opener()
        self.https = https
    
    def request(self, host, handler, request_body, verbose=0):
        proto = ('http', 'https')[bool(self.https)]
        req = urllib2.Request('%s://%s%s' % (proto, host, handler), request_body)
        req.add_header('User-agent', self.user_agent)
        self.verbose = verbose
        return self.parse_response(self.opener.open(req))


class HTTPProxyTransport(Urllib2Transport):
    def __init__(self, proxies, use_datetime=0):
        opener = urllib2.build_opener(urllib2.ProxyHandler(proxies))
        Urllib2Transport.__init__(self, opener, use_datetime)
