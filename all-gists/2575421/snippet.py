# adapted from https://code.google.com/p/wsgi-proxy
from httplib import HTTPConnection
from urlparse import urlparse
import copy
import logging
import mimetypes
import os


_hoppish = {
    'connection':1, 'keep-alive':1, 'proxy-authenticate':1,
    'proxy-authorization':1, 'te':1, 'trailers':1, 'transfer-encoding':1,
    'upgrade':1, 'proxy-connection':1 }


def is_hop_by_hop(header):
    return _hoppish.has_key(header.lower())



class WSGIProxyApplication(object):
    """Application to handle requests that need to be proxied"""

    ConnectionClass = HTTPConnection

    def __init__(self, allowed_hosts=None, localdir=os.curdir):
        if allowed_hosts is None:
            self.allowed_hosts = ['localhost', '127.0.0.1', 'pypi.python.org']
        else:
            self.allowed_hosts = allowed_hosts
        self.localdir = localdir

    def reconstruct_url(self, environ):
        # From WSGI spec, PEP 333
        url = scheme = environ['wsgi.url_scheme'] + '://'
        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']
            if environ['wsgi.url_scheme'] == 'https':
                if environ['SERVER_PORT'] != '443':
                    url += ':' + environ['SERVER_PORT']
            else:
                if environ['SERVER_PORT'] != '80':
                    url += ':' + environ['SERVER_PORT']

        url += environ.get('SCRIPT_NAME','')
        path_info = environ.get('PATH_INFO','')
        if path_info.startswith(scheme):
            path_info = urlparse(path_info)
            url += path_info.path
        else:
            url += path_info

        # Fix ;arg=value in url
        if url.find('%3B') is not -1:
            url, arg = url.split('%3B', 1)
            url = ';'.join([url, arg.replace('%3D', '=')])
        # Stick query string back in
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']

        environ['reconstructed_url'] = url
        return url

    def handler(self, environ, start_response):
        """Proxy for requests to the actual http server"""
        ourl = self.reconstruct_url(environ)
        url = urlparse(ourl)

        # are we allowed to go there ?
        if url.netloc not in self.allowed_hosts:
            # no.

            if (url.path.endswith('.egg') or
                url.path.endswith('.gz') or
                url.path.endswith('.zip')):
                # do we have a local fallback ?
                mtype = mimetypes.guess_type(url.path)

                filename = os.path.join(self.localdir, url.path.split('/')[-1])
                if os.path.exists(filename):    #  security ? (../)
                    # serve the file
                    start_response("200 OK", [('Content-Type', mtype[0])])
                    with open(filename) as f:
                        return [f.read()]

            # no
            print('*** %s BLOCKED' % ourl)
            start_response("404 Not Found", [('Content-Type', 'text/html')])
            return ['<H1>The Proxy service blocked this call</H1>']

        # Create connection object
        try:
            connection = self.ConnectionClass(url.netloc)
            # Build path
            path = url.geturl().replace('%s://%s' % (url.scheme, url.netloc), '')
        except Exception, e:
            start_response("501 Gateway error", [('Content-Type', 'text/html')])
            return ['<H1>Could not connect</H1>']


        # Read in request body if it exists
        body = None
        if environ.get('CONTENT_LENGTH'):
            length = int(environ['CONTENT_LENGTH'])
            body = environ['wsgi.input'].read(length)


        # Build headers
        headers = {}
        for key in environ.keys():
            # Keys that start with HTTP_ are all headers
            if key.startswith('HTTP_'):
                # This is a hacky way of getting the header names right
                value = environ[key]
                key = key.replace('HTTP_', '', 1).swapcase().replace('_', '-')
                if is_hop_by_hop(key) is False:
                    headers[key] = value

        # Handler headers that aren't HTTP_ in environ
        if environ.get('CONTENT_TYPE'):
            headers['content-type'] = environ['CONTENT_TYPE']

        # Add our host if one isn't defined
        if not headers.has_key('host'):
            headers['host'] = environ['SERVER_NAME']

        # Make the remote request
        try:
            connection.request(environ['REQUEST_METHOD'], path, body=body, headers=headers)
        except:
            # We need extra exception handling in the case the server fails in mid connection, it's an edge case but I've seen it
            start_response("501 Gateway error", [('Content-Type', 'text/html')])
            return ['<H1>Could not connect</H1>']

        response = connection.getresponse()

        hopped_headers = response.getheaders()
        headers = copy.copy(hopped_headers)
        for header in hopped_headers:
            if is_hop_by_hop(header[0]):
                headers.remove(header)

        start_response(response.status.__str__()+' '+response.reason, headers)
        return [response.read(response.length)]


    def __call__(self, environ, start_response):
        return self.handler(environ, start_response)


if __name__ == '__main__':
    from wsgiref import simple_server
    application = WSGIProxyApplication()
    server = simple_server.make_server('localhost', 8080, application)
    print 'serving on port 8080'
    server.serve_forever()
