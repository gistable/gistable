import os
import re
import SimpleHTTPServer
import SocketServer
import sys

port = 8080
if len(sys.argv) == 2:
    port = int(sys.argv[1])
elif len(sys.argv) > 2:
    print "Usage:", sys.argv[0], "[port]"
    sys.exit(1)

p = os.popen('ifconfig',"r")
while 1:
    line = p.readline()
    if not line: break
    m = re.search('inet ([^ ]+) ', line)
    if m and m.group(1):
        addr = m.group(1)
        if addr != '127.0.0.1':
            print 'Listening on', 'http://' + addr + ':' + str(port)
p.close()

class SimpleServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True
    def __init__(self, port):
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        SocketServer.TCPServer.__init__(self, ('', port), handler)

httpd = SimpleServer(port)
try:
    httpd.serve_forever()
except:
    pass
