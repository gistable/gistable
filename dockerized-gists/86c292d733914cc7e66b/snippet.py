import asyncio
import time

HOST = "localhost"
PORT = 8888


class Client(asyncio.Protocol):
    def __init__(self, message, loop, host, port):
        self.message = message
        self.loop = loop
        self.host = host
        self.port = port
        self.connected = False

    def connection_made(self, transport):
        self.connected = True
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        self.connected = False
        print('The server closed the connection')
        print('reconnect')
        self.reconnect(5)

    def __call__(self):
        # Protocol factory. Called by loop.create_connection
        return self

    def excetpion_handler(self, loop, context):
        # exc = context['exception']
        if not self.connected:
            print('Could not connect.')
            self.reconnect(5)
        self.connected = False

    def reconnect(self, delay):
        self.loop.call_later(delay, self.connect, self.message,
                             self.loop, self.host, self.port)

    @classmethod
    def connect(cls, message, loop, host, port):
        print('trying to connect to {}:{}'.format(host, port))
        client = cls(message, loop, host, port)
        loop.set_exception_handler(client.excetpion_handler)
        coro = loop.create_connection(client, HOST, PORT)
        asyncio.ensure_future(coro)
        return client


def main():
    loop = asyncio.get_event_loop()
    Client.connect('Hello World!', loop, HOST, PORT)
    loop.run_forever()


if __name__ == '__main__':
    main()
