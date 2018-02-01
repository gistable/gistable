import SocketServer
from gevent import monkey
monkey.patch_socket(dns=False)
import requests
from dnslib import *

cache = {'0bad.com': ['69.163.160.212'], 'bitstress.com': ['127.0.0.1']}


def redirect_ip(data, ip='144.214.121.220'):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # query the official server
    s.sendto(data, (ip, 53))
    data, server = s.recvfrom(2048)
    s.close()
    # parse reply
    #reply = DNSRecord.parse(data)
    #ips = [str(rr.rdata) for rr in reply.rr]
    #print 'from school'#, ip, ips
    return data


def redirect_tcp(data, ip='8.8.8.8'):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((ip, 53))
    s.sendall(data)
    data = s.recv(2048)
    s.close()
    return data


def redirect_0bad(data, request):
    id, qname, qtype = request.header.id, request.q.qname, request.q.qtype
    domain = str(qname)

    # if relate to school, redirect to the official server
    if domain.endswith('.edu.hk'):
        return redirect_ip(data)

    # construct reply
    reply = DNSRecord(DNSHeader(id=id, qr=1, aa=1, ra=1), q=request.q)

    # fix
    data = redirect_ip(data)
    reply = DNSRecord.parse(data)
    for r in reply.rr:
        if r.rtype != QTYPE.A:
            reply.add_answer(r)

    if qtype == QTYPE.A:
        # query the 0bad.com
        if domain not in cache:
            text = requests.get('http://0bad.com/?dm='+domain).text
            text = text.strip().replace('<pre>', '').replace('</pre>', '')
            lines = [l.split() for l in text.split('\n') if l]
            lines = [l for l in lines if l[-2] == 'A']
            ips = [l[-1] for l in lines]
            cache[domain] = ips
        else:
            ips = cache[domain]
        print ips
        for ip in ips:
            reply.add_answer(RR(qname, qtype, rdata=A(ip)))
        return reply.pack()
    else:
        # else, query the official server
        return redirect_ip(data)


class ServerHandler(SocketServer.BaseRequestHandler):
    daemon_threads = True
    allow_reuse_address = True

    def handle(self):
        data = self.request[0]
        socket = self.request[1]
        addr = self.client_address
        request = DNSRecord.parse(data)
        qname, qtype = request.q.qname, request.q.qtype
        print '\nrequest: {} {}'.format(str(qname), QTYPE[qtype])
        #data = redirect_ip(data)
        #data = redirect_tcp(data)
        data = redirect_0bad(data, request)
        socket.sendto(data, addr)


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    def __init__(self, s, t):
        SocketServer.UDPServer.__init__(self, s, t)


def main():
    try:
        server = ThreadedUDPServer(('127.0.0.1', 53), ServerHandler)
    except Exception as e:
        print "Failed to create socket on UDP port 53:", e
        exit(1)
    print 'start listening on 53 ...'
    server.serve_forever()
    server.shutdown()

if __name__ == '__main__':
    main()