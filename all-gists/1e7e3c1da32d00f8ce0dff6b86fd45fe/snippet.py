#!/usr/bin/env python3

import os
import html
import urllib
import sys
import http
import cgi
import socket
import socketserver
import mimetypes
from io import BytesIO
from http import HTTPStatus
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
import netifaces as ni

__version__ = "0.8"

class UploadHTTPHandler(SimpleHTTPRequestHandler):

    server_version = "SimpleHTTP/" + __version__

    def do_POST(self):
        """Serve a POST request."""
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })
        filename = form['file'].filename
        path = self.translate_path(self.path)
        filepath = os.path.join(path, filename)
        if os.path.exists(filepath):
            self.log_error('File %s exist!', filename)
            filepath += '.new'

        with open(filepath, 'wb') as f:
            f.write(form['file'].value)
        super().do_GET()

    def list_directory(self, path):

        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath)
        enc = sys.getfilesystemencoding()
        title = 'Directory listing for %s' % displaypath
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('''<form action="" enctype="multipart/form-data" method="post">\n
                    <input name="file" type="file" />
                    <input value="upload" type="submit" />
                </form>''')
        r.append('<hr>\n<ul>')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            r.append('<li><a href="%s">%s</a></li>'
                    % (urllib.parse.quote(linkname,
                                          errors='surrogatepass'),
                       html.escape(displayname)))
        r.append('</ul>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')
        f = BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })


def get_httpd(port):
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    return httpd

def get_wirelessip(interf):
    try:
        wirelessip = ni.ifaddresses(interf)[ni.AF_INET][0]['addr']
    except:
        wirelessip = get_ip_address()

    return wirelessip

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

def show_qr(url):
    cmd = "echo {} | qrencode -o - -t UTF8".format(url)
    os.system(cmd)

if __name__ == '__main__':
    #"""with upload
    if len(sys.argv) == 3:
        webdir=sys.argv[1]
        port=int(sys.argv[2])
        os.chdir(webdir)

        UploadHTTPHandler.protocol_version = "HTTP/1.0"
        wirelessip = get_wirelessip("en0")
        server_address = (wirelessip, port)
        httpd = HTTPServer(server_address, UploadHTTPHandler)
        sa = httpd.socket.getsockname()

        url = "http://{}:{}".format(sa[0], sa[1])
        show_qr(url)
        print(" | Serving HTTP on {}".format(url))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received, exiting.")
            httpd.server_close()
            sys.exit(0)
    else:
        print ("Usage:\n\t{} WEB_DIR PORT".format(sys.argv[0]))
    """wo upload
    if len(sys.argv) == 3:
        WEB_DIR=sys.argv[1]
        port=int(sys.argv[2])

        os.chdir(WEB_DIR)
        wirelessip = get_wirelessip("en0")
        httpd = get_httpd(port)
        url = "http://{}:{}".format(wirelessip, port)

        show_qr(url)
        print (" | Serving at {}".format(url))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n | Keyboard interrupt received, exiting.")
            httpd.server_close()
            sys.exit(0)
    else:
        print ("Usage:\n\t{} WEB_DIR PORT".format(sys.argv[0]))
    """