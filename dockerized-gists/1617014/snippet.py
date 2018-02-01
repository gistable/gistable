#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTTP server that provides a web interface to run "tail" on a file,
like the Unix command.

This is a standalone script. No external dependencies required.

How to invoke:

    python webtail.py filename [port]

Where:

    - filename is the name of the file to "tail" (as in Unix tail).
    - port is the port number where the webtail server will listen.

"""

__version__ = '0.1.1'
__author__ = 'Santiago Coffey'
__email__ = 'scoffey@itba.edu.ar'

import BaseHTTPServer
import SocketServer
import collections
import logging
import os
import sys
import urlparse

_STATIC_HTML = """<html>
<head>
<title>Web Tail</title>
<script type="text/javascript">

var offset = 0;
var polling = null;

var param = function (key, fallback) {
    var query = window.location.search.substring(1);
    var parameters = query.split('&');
    for (var i = 0; i < parameters.length; i++) {
        var pair = parameters[i].split('=');
        if (pair[0] == key) {
            return unescape(pair[1]);
        }
    }
    return fallback;
}

var append = function (text) {
    if (text) {
        var element = document.getElementById('tail');
        element.textContent += text;
        window.scrollTo(0, document.body.scrollHeight);
    }
}

var request = function (uri, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', uri, true);
    xhr.onreadystatechange = function () {
        var done = 4, ok = 200;
        if (xhr.readyState == done && xhr.status == ok) {
            var newOffset = xhr.getResponseHeader('X-Seek-Offset');
            if (newOffset) offset = parseInt(newOffset);
            callback(xhr.responseText);
        }
    };
    xhr.send(null);
}

var tail = function () {
    var uri = '/tail?offset=' + offset;
    if (!offset) {
        var limit = parseInt(param('limit', 1000));
        uri += '&limit=' + limit;
    }
    request(uri, append);
}

var refresh = function () {
    tail();
    if (polling == null) {
        var interval = parseInt(param('interval', 3000));
        polling = window.setInterval(tail, interval);
    }
}

var sleep = function () {
    if (polling != null) {
        window.clearInterval(polling);
        polling = null;
    }
}

window.onload = refresh;
window.onfocus = refresh;
window.onblur = sleep;

</script>
</head>

<body style="background: black; color: #ddd;">
<pre id="tail"></pre>
</body>

</html>
"""

class WebTailHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ Request handler for the web tail server """

    protocol_version = 'HTTP/1.1'

    filename = None # determines file to tail

    def do_GET(self):
        self.http_headers = {}
        routes = {
            '/': lambda request: _STATIC_HTML,
            '/tail': self._get_tail
        }
        try:
            url = urlparse.urlsplit(self.path)
            request = dict(urlparse.parse_qsl(url.query))
            if url.path in routes:
                handler = routes[url.path]
                body = handler(request)
                self._serve(body, 200)
            else: # not found
                self._serve('', 400)
        except Exception:
            logging.exception('Failed to handle request at %s', self.path)
            self._serve('', 500)

    def _get_tail(self, request):
        size = os.stat(self.filename).st_size
        self.http_headers['Content-Type'] = 'text/plain'
        self.http_headers['X-Seek-Offset'] = str(size)
        offset = int(request.get('offset', 0))
        limit = int(request.get('limit', 0)) or None
        if size <= offset:
            logging.info('tail returned empty string with stat optimization')
            return ''
        new_offset, lines = self.tail(self.filename, offset, limit)
        logging.info('tail(%r, %r, %r) returned offset %d and %d lines', \
                self.filename, offset, limit, new_offset, len(lines))
        self.http_headers['X-Seek-Offset'] = str(new_offset)
        return ''.join(lines)

    def _serve(self, body, http_status=200):
        self.send_response(http_status)
        self.http_headers.setdefault('Content-Type', 'text/html')
        self.http_headers.setdefault('Content-Length', len(body))
        self.http_headers.setdefault('Connection', 'keep-alive')
        for k, v in self.http_headers.iteritems():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def tail(self, filename, offset=0, limit=None):
        """ Returns lines in a file (from given offset, up to limit lines) """
        lines = collections.deque([], limit)
        stream = open(filename)
        stream.seek(offset)
        for line in stream:
            if not line.endswith('\n'): # ignore last line if incomplete
                break
            lines.append(line)
            offset += len(line)
        stream.close()
        return (offset, lines)

    def log_request(self, code='-', size='-'):
        pass

class WebTailServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """ Web tail server.

        Only differs from BaseHTTPServer.HTTPServer in the handling of
        exceptions while processing requests. """

    def _handle_request_noblock(self):
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except KeyboardInterrupt:
                self.close_request(request)
                raise # pass on interruption in order to stop server
            except Exception:
                self.handle_error(request, client_address)
                self.close_request(request)

    def handle_error(self, request, client_address):
        logging.exception('Error while processing request from %s:%d', \
                *client_address)

def main(program, filename=None, port=7411, **kwargs):
    """ Main program: Runs the web tail HTTP server """
    if filename is None:
        logging.error('No input file to tail')
        return
    try:
        WebTailHTTPRequestHandler.filename = filename
        server_address = ('', int(port))
        httpd = WebTailServer(server_address, WebTailHTTPRequestHandler)
        logging.info('Starting HTTP server at port %d', server_address[1])
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info('HTTP server stopped')

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, \
            format='[%(asctime)s] [%(levelname)s] %(message)s')
    main(*sys.argv)
