
import signal

from rose import EventLoopPolicy
from tulip import events, protocols

events.set_event_loop_policy(EventLoopPolicy())


class EchoProtocol(protocols.Protocol):
    def connection_made(self, transport):
        # TODO: Transport should probably expose getsockname/getpeername
        print("Client connected: {}".format(transport._sock.getpeername()))
        self.transport = transport
    def data_received(self, data):
        self.transport.write(data.upper())
    def eof_received(self):
        self.transport.close()
    def connection_lost(self, exc):
        print("Client closed connection")


reactor = events.get_event_loop()

f = reactor.start_serving(EchoProtocol, '127.0.0.1', 1234)
server_socket = reactor.run_until_complete(f)
print("Serving on {}".format(server_socket.getsockname()))
reactor.add_signal_handler(signal.SIGINT, reactor.stop)

reactor.run()
