#!/usr/bin/env python3

import asyncio
import multiprocessing
import os
import ssl
from time import sleep

port = 9000

def main():
    # Command to generate the self-signed key:
    #
    #     openssl req -x509 -newkey rsa:2048 -keyout selfsigned.key -nodes \
    #                 -out selfsigned.cert -sha256 -days 1000
    #
    # use 'localhost' as Common Name
    assert os.path.isfile('selfsigned.cert')
    server_process = multiprocessing.Process(target=server, name='server')
    server_process.start()
    try:
        sleep(.5)
        client_process = multiprocessing.Process(target=client, name='client')
        client_process.start()
        try:
            client_process.join(1)
            assert not client_process.is_alive()
        finally:
            client_process.terminate()
            client_process.join()
    finally:
        server_process.terminate()
        server_process.join()


def server():

    @asyncio.coroutine
    def handle_connection(reader, writer):
        addr = writer.get_extra_info('peername')
        data = yield from reader.readline()
        print("Server received {!r} from {}".format(data, addr))
        assert data == b'ping\n', repr(data)
        writer.write(b'pong\n')
        yield from writer.drain()
        writer.close()
        print('Server done')

    sc = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    sc.load_cert_chain('selfsigned.cert', 'selfsigned.key')

    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_connection, '127.0.0.1', port, ssl=sc, loop=loop)
    server = loop.run_until_complete(coro)

    print('Serving on {}'.format(server.sockets[0].getsockname()))
    loop.run_forever()


def client():

    @asyncio.coroutine
    def tcp_echo_client(loop):
        sc = ssl.create_default_context(ssl.Purpose.SERVER_AUTH,
            cafile='selfsigned.cert')

        reader, writer = yield from asyncio.open_connection(
            'localhost', port, ssl=sc, loop=loop)
        writer.write(b'ping\n')
        yield from writer.drain()
        data = yield from reader.readline()
        assert data == b'pong\n', repr(data)
        print("Client received {!r} from server".format(data))
        writer.close()
        print('Client done')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(tcp_echo_client(loop))
    loop.close()


if __name__ == '__main__':
    main()