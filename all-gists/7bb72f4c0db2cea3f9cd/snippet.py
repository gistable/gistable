#!/usr/bin/env python

# source: http://www.joedog.org/pub/AJP/ajping.txt

from struct import unpack
import time
import sys
import socket

acks = set([65, 66, 0, 1, 9])

HOST = None
PORT = None

if len(sys.argv) == 3:
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    pass
elif len(sys.argv) == 2:
    tmp = sys.argv[1].split(':', 2)
    HOST = tmp[0]
    PORT = tmp[1]
else:
    print "Host and/or port missing or incorrect"
    print "Usage:"
    print "  python ajping.py <host>:<port>"
    print "  python ajping.py <host> <port>"
    sys.exit(1)

for i in range(10):
    start = time.time()

    s = None
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except socket.error as msg:
            s = None
            continue
        try:
            s.connect(sa)
        except socket.error as msg:
            s.close()
            s = None
            continue
        break
    if s is None:
        print 'could not open socket'
        sys.exit(1)
    s.send(bytearray([0x12, 0x34, 0x00, 0x01, 0x0a]))
    data = s.recv(5)
    s.close()

    if not len(data) == 5:
        print "Protocol error: unable to verify AJP host {0}:{1}".format(HOST, PORT)
        sys.exit(1)

    vals = set([ord(i) for i in unpack('5c', data)])
    if len(acks.intersection(vals)) == len(acks):
        # all acks are in the answer, so everything is ok
        print "Reply from {0}: {1} bytes in {2:3.3f} seconds".format(HOST, len(data), time.time() - start)
    else:
        print "Protocol error: unable to verify AJP host {0}:{1}".format(HOST, PORT)
        sys.exit(1)
    time.sleep(1)

sys.exit(0)
