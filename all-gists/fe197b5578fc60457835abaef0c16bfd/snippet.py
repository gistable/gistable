import asyncio
import socket
import struct


SO_ORIGINAL_DST = 80


class NATCPServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.src = peername = transport.get_extra_info('peername')
        self.sock = sock = transport.get_extra_info('socket')
        self.dst = self.get_dst_from_socket(sock)
        print('Connection from {} to {}.'.format(peername, self.dst))

        self.transport = transport
        self.buffer = b''
        self.closed = False

        self.client = NATCPClientProtocol(self)

        asyncio.ensure_future(self.setup_client())


    def data_received(self, data):
        if not hasattr(self.client, 'transport'):
            self.buffer += data
        else:
            self.client.transport.write(data)

    def connection_lost(self, exc):
        if hasattr(self.client, 'transport'):
            self.client.transport.close()
            self.closed = True
        print('Client closed the connection from {} to {}.'.format(self.src, self.dst))

    def get_dst_from_socket(self, sock):
        dst_info = sock.getsockopt(socket.SOL_IP, SO_ORIGINAL_DST, 16)
        port, ip = self.port_and_ip_struct.unpack(dst_info)
        ip = socket.inet_ntoa(ip)
        return ip, port

    async def setup_client(self):
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_IP, socket.IP_TRANSPARENT, 1)
        sock.bind((self.src[0], 0))
        sock.setblocking(False)
        await loop.sock_connect(sock, self.dst)
        await loop.create_connection(lambda: self.client, sock=sock)

    port_and_ip_struct = struct.Struct('!2xH4s8x')


class NATCPClientProtocol(asyncio.Protocol):
    def __init__(self, server):
        self.server = server

    def connection_made(self, transport):
        if self.server.closed:
            transport.close()
        else:
            self.transport = transport
            self.transport.write(self.server.buffer)
            self.server.buffer = b''

    def data_received(self, data):
        self.server.transport.write(data)

    def connection_lost(self, exc):
        print('Remote server closed the connection from {} to {}.'.format(self.server.src, self.server.dst))
        self.server.transport.close()


loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(NATCPServerProtocol, '0.0.0.0', 2334)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
