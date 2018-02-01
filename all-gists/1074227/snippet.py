# dns server using dnslib and gevent
# based on https://bitbucket.org/paulc/dnslib/src/80d85555aae4/src/server/gevent_server.py
# set the key as
# set IP:name ip_addr
# set TXT:name txtfield
# fallback on gevent's dns resolver
# gleicon 2011


import gevent
from gevent import socket
import gevent.dns;
from gevent import monkey;
monkey.patch_socket()

import urllib2,sys
import redis
import random
from dnslib import *


AF_INET = 2
SOCK_DGRAM = 2

s = socket.socket(AF_INET,SOCK_DGRAM)
s.bind(('',53))

def dns_handler(s, peer, data, r):
    request = DNSRecord.parse(data)
    id = request.header.id
    qname = request.q.qname
    qtype = request.q.qtype
    IP = r.get("IP:%s" % qname)
    TXT = r.get("TXT:%s" % qname)
    if not IP:
        try:
            IP = socket.gethostbyname(str(qname))
        except Exception, e:
            print 'Host not found'
            IP = '0.0.0.0'
    print "Request (%s): %r (%s) - Response: %s" % (str(peer), qname.label, QTYPE[qtype], IP)
    reply = DNSRecord(DNSHeader(id=id,qr=1,aa=1,ra=1),q=request.q)
    if qtype == QTYPE.A:
        reply.add_answer(RR(qname,qtype,rdata=A(IP)))
    elif qtype == QTYPE['*']:
        reply.add_answer(RR(qname,QTYPE.A,rdata=A(IP)))
        reply.add_answer(RR(qname,QTYPE.MX,rdata=MX(IP)))
        reply.add_answer(RR(qname,QTYPE.TXT,rdata=TXT(TXT)))
    else:
        reply.add_answer(RR(qname,QTYPE.CNAME,rdata=CNAME(TXT)))
    s.sendto(reply.pack(),peer)


def main():
    r = redis.Redis()
    while True:
        data,peer = s.recvfrom(8192)
        gevent.spawn(dns_handler, s, peer, data, r)

if __name__ == '__main__':
    main()
