import select
import socket


class EchoServer(object):
    def __init__(self, reactor):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', 8000))
        self.sock.listen(2)
        self.reactor = reactor

    def fileno(self):
        return self.sock.fileno()

    def on_read(self):
        conn, _ = self.sock.accept()
        EchoClient(conn, self.reactor)

class EchoClient(object):
    def __init__(self, sock, reactor):
        self.sock = sock
        self.sock.setblocking(False)
        self.reactor = reactor
        self.reactor.register_for_read(self)
        self.buffer = ''

    def fileno(self):
        return self.sock.fileno()

    def on_read(self):
        data = self.sock.recv(1000)
        self.buffer += data
        if not data:
            self.sock.close()
        else:
            self.reactor.register_for_read(self)
            self.reactor.register_for_write(self)

    def on_write(self):
        sent = self.sock.send(self.buffer)
        self.buffer = self.buffer[sent:]
        if self.buffer:
            self.reactor.register_for_write(self)


class Reactor(object):
    def __init__(self):
        self.want_to_read = []
        self.want_to_write = []

    def register_for_read(self, thing):
        self.want_to_read.append(thing)

    def register_for_write(self, thing):
        self.want_to_write.append(thing)

    def loop(self):
        print self.want_to_read
        rs, ws, xs = select.select(self.want_to_read, self.want_to_write, [])
        for r in rs:
            self.want_to_read.remove(r)
            r.on_read()
        for w in ws:
            self.want_to_write.remove(w)
            w.on_write()

def main():
    r = Reactor()
    server = EchoServer(r)
    r.register_for_read(server)
    while True:
        r.loop()

main()





