#!/usr/bin/env python


from circuits.net.events import write
from circuits import handler, Component, Debugger
from circuits.net.sockets import TCPServer, UDPServer


class UDPTCPBroadcaster(Component):

    def init(self):
        self.clients = {}
        self.tcp = TCPServer(("0.0.0.0", 7001), channel="tcp").register(self)
        self.udp = UDPServer(("0.0.0.0", 7000), channel="udp").register(self)

    def broadcast(self, data, exclude=None):
        exclude = exclude or []
        targets = (sock for sock in self.clients.keys() if sock not in exclude)
        for target in targets:
            self.fire(write(target, data), "tcp")

    @handler("connect", channel="tcp")
    def _on_tcp_connect(self, sock, host, port):
        self.clients[sock] = {"host": sock, "port": port}

    @handler("disconnect", channel="tcp")
    def _on_tcp_disconnect(self, sock):
        if sock not in self.clients:
            return

        del self.clients[sock]

    @handler("read", channel="tcp")
    def _on_tcp_read(self, sock, data):
        data = data.strip().decode("utf-8")

        print sock, data

    @handler("read", channel="udp")
    def _on_udp_read(self, peer, data):
        # Broadcast to all connected TCP clients
        self.broadcast(data)


app = UDPTCPBroadcaster()
Debugger().register(app)
app.run()
