#!/usr/bin/env python3
'''Usage:
    python3 http-stdout-echo.py -a <bind-address> -p <bind-port>
    
   Examples:
    python3 http-stdout-echo.py # (will listen at 127.0.0.1:8080 by default)
    python3  http-stdout-echo.py -a 10.3.1.3 -p 5555'''

from http.server import HTTPServer, BaseHTTPRequestHandler

class DummyHTTPHandler(BaseHTTPRequestHandler):
    '''Simple HTTP server. Print to stdout every requests made to it.
    Useful for development or debbuging... At least for me!'''
    
    def do_GET(self):
        print('{} - {} - {}'.format(self.client_address, self.request_version, self.path))
        print('\n### Headers ###\n'+ str(self.headers))
        self.send_response(200, "GET successfuly served!")
        self.end_headers()
    
    def do_POST(self):
        msg_length = int(self.headers['Content-Length'])
        print('{} - {} - {}'.format(self.client_address, self.request_version, self.path))
        print('\n### Headers ###\n'+ str(self.headers))
        print('\n### POST content ###\n{}'.format(self.rfile.read(msg_length)))
        self.send_response(200, "POST successfully served!")
        self.end_headers()
        
if __name__ == '__main__':
    import argparse

    #Command line argument handling:
    parser = argparse.ArgumentParser(description='Dummy HTTP server. Prints everything to stdout')
    parser.add_argument('-a', '--address', help='default: 127.0.0.1')
    parser.add_argument('-p', '--port', help='default: 8080', type=int)
    args = parser.parse_args()

    server = HTTPServer((args.address or '127.0.0.1', args.port or 8080), DummyHTTPHandler)
    server.serve_forever()
