import SimpleHTTPServer
import SocketServer

paths = set()


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Detect remote file inclusion
        if '=http' in self.path:
            print 'RFI detected'
            # TODO: Add RFI handler here
        # Detect local file inclusion
        elif '../../' in self.path:
            print 'LFI detected'
            # TODO: Add LFI handler here
        # Collect dorks from attacks
        paths.add('<a href="{}">a link?</a><br />'.format(self.path))
        # Compose the attack surface, adding all dorks
        http_doc = """
        <html>
        <style>
        a:link, a:visited, a:active, a:hover{{
            color:#000000;
            text-decoration:none;
            cursor:text;
        }}
        </style>
        is there
        <a href='http://google.com'>a link?</a><br />
        {}
        </html>
        """.format(
            ''.join(paths)
        )
        # Send response
        self.wfile.write(http_doc)


if __name__ == '__main__':
    SocketServer.TCPServer.allow_reuse_address = True
    httpd = SocketServer.TCPServer(('localhost', 8080), Handler)
    print "Serving at port 8080"
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print 'bye'
