import asyncore
import errno
import os
import socket
import logging
import threading

log = logging.getLogger('tcp_proxy')

_map = {}

class FixedDispatcher(asyncore.dispatcher):
    def handle_error(self):
        # Default error handling is just pathetic. Just raise the
        # fracking exception, is it so hard?
        log.error(exc_info=True)
        raise

class JustRecvSock(FixedDispatcher):
    def handle_read(self):
        print 'x'
        self.recv(4096)

class Sock(FixedDispatcher):
    write_buffer = ''
    def readable(self):
        return not self.other.write_buffer

    def handle_read(self):
        self.other.write_buffer += self.recv(4096*4)

    def handle_write(self):
        sent = self.send(self.write_buffer)
        self.write_buffer = self.write_buffer[sent:]

    def handle_close(self):
        log.info(' [-] %i -> %i (closed)' % \
                     (self.getsockname()[1], self.getpeername()[1]))
        self.close()
        if self.other.other:
            self.other.close()
            self.other = None

class Server(FixedDispatcher):
    def __init__(self, dst_port, src_port=0, map=None):
        self.dst_port = dst_port
        self.map = map
        asyncore.dispatcher.__init__(self, map=self.map)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('localhost', src_port))
        self.src_port = self.getsockname()[1]
        log.info(' [*] Proxying %i ==> %i' % \
                     (self.src_port, self.dst_port))
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if not pair:
            return
        left, addr = pair
        try:
            right = socket.create_connection(('localhost', self.dst_port))
        except socket.error, e:
            if e.errno is not errno.ECONNREFUSED: raise
            log.info(' [!] %i -> %i ==> %i refused' % \
                         (addr[1], self.src_port, self.dst_port))
            left.close()
        else:
            log.info(' [+] %i -> %i ==> %i -> %i' % \
                         (addr[1], self.src_port,
                          right.getsockname()[1], self.dst_port))
            a, b = Sock(left, map=self.map), Sock(right, map=self.map)
            a.other, b.other = b, a

    def close(self):
        log.info(' [*] Closed %i ==> %i' % \
                     (self.src_port, self.dst_port))
        asyncore.dispatcher.close(self)


# server1 = Server(src_port=49620, dst_port=820, map=_map)
# server2 = Server(src_port=49621, dst_port=80, map=_map)
# asyncore.loop(map=self.map)


class AsyncoreRunner(threading.Thread):
    def __init__(self, map):
        self.map = map
        read, write = socket.socketpair()
        self.X = JustRecvSock(read, map=self.map)
        self.write = write
        threading.Thread.__init__(self)

    def ping(self):
        self.write.send('x')

    def run(self):
        print ' thread start'
        asyncore.loop(map=self.map)
        print ' thread stop'

    def close(self):
        self.write.close()
        self.join()



class AmqpProxy(object):
    def __init__(self):
        self.srv = Server(dst_port=5672, ar=None)
        self.port = self.srv.src_port
        self.ar = ar
        self.ar.ping()

    def close(self):
        self.srv.close()
        self.srv = None
        self.ar.ping()

    def reopen(self):
        self.srv = Server(src_port=self.port, dst_port=5672, map=self.ar.map)
        self.ar.ping()

    def __str__(self):
        return 'amqp://localhost:%s' % (self.port,)

class Proxy(object):
    def __init__(self):
        self._map = {}
        self.ar = AsyncoreRunner(self._map)
        self.ar.start()

    def close(self):
        self.ar.close()
        self.ar = None

    def AmqpProxy(self):
        return AmqpProxy(ar=self.ar)

if __name__ == '__main__':
    import time
    time.sleep(1)

    x = AmqpProxy()
    print x
    time.sleep(1)
    x.close()
    time.sleep(1)
    ar.close()
