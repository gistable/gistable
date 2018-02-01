
#!/usr/bin/python

# simplified from msocks5.py @ https://github.com/felix021/ssocks5

import sys 
import signal

try:
    import gevent
    from gevent import socket
    from gevent.server import StreamServer
    from gevent.socket import create_connection, gethostbyname
except:
    print >>sys.stderr, "please install gevent first!"
    sys.exit(1)

class XSocket(gevent.socket.socket):
    def __init__(self, socket = None, addr = None):
        if socket is not None:
            gevent.socket.socket.__init__(self, _sock = socket)
        elif addr is not None:
            gevent.socket.socket.__init__(self)
            self.connect(addr)
        else:
            raise Exception("XSocket.init: bad arguments")

    def forward(self, dest):
        try:
            while True:
                try:
                    data = self.recv(1024)
                    if not data:
                        break
                    dest.sendall(data)
                except socket.error, e:
                    print e
                    break
        finally:
            self.close()
            dest.close()

class SocksServer(StreamServer):
    def handle(self, sock, addr):
        print 'connection from %s:%s' % addr

        src = XSocket(socket = sock)

        try:
            dest = XSocket(addr = self.remote)
        except IOError, ex:
            print "%s:%d" % addr, "failed to connect to %s:%d" % remote
            return

        gevent.spawn(src.forward, dest)
        gevent.spawn(dest.forward, src)

    def close(self):
        sys.exit(0)

    def set_remote(self, remote_host, remote_port):
        self.remote = (remote_host, remote_port)

    @staticmethod
    def start_server(local_port, remote_host, remote_port):
        local = ('0.0.0.0', local_port) 
        server = SocksServer(local)
        server.set_remote(remote_host, remote_port)
        gevent.signal(signal.SIGTERM, server.close)
        gevent.signal(signal.SIGINT, server.close)
        print "Server is listening on %s:%d" % local
        server.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print >>sys.stderr, "%s <local_port> <remote_host> <remote_port>" % sys.argv[0]
        sys.exit(1)
    local_port = int(sys.argv[1])
    remote_host = sys.argv[2]
    remote_port = int(sys.argv[3])
    SocksServer.start_server(local_port, remote_host, remote_port)