import SimpleHTTPServer
import SocketServer
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class MyHandler(BaseHTTPRequestHandler):

    def handle_request(self):
        try:
            print "New request received: ", self.path
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            self.wfile.write('OK')
            return
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

def main():
    PORT = 8000
    try:
        server = HTTPServer(('', PORT), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()
