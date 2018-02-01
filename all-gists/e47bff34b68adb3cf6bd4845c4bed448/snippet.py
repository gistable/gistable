"""Provide high-level UDP endpoints for asyncio"""

__all__ = ['open_local_endpoint', 'open_remote_endpoint']

import asyncio
import warnings


class DatagramEndpointProtocol(asyncio.DatagramProtocol):

    def __init__(self, endpoint):
        self._endpoint = endpoint

    # Protocol methods

    def connection_made(self, transport):
        self._endpoint._transport = transport

    def connection_lost(self, exc):
        if exc is not None:
            msg = 'Endpoint lost the connection: {!r}'
            warnings.warn(msg.format(exc))
        self._endpoint.close()

    # Datagram protocol methods

    def datagram_received(self, data, addr):
        self._endpoint.feed_datagram(data, addr)

    def error_received(self, exc):
        msg = 'Endpoint received an error: {!r}'
        warnings.warn(msg.format(exc))


class Endpoint:

    def __init__(self, queue_size=None):
        if queue_size is None:
            queue_size = 0
        self._queue = asyncio.Queue(queue_size)
        self._closed = False
        self._transport = None

    # Protocol callbacks

    def feed_datagram(self, data, addr):
        try:
            self._queue.put_nowait((data, addr))
        except asyncio.QueueFull:
            warnings.warn('Endpoint queue is full')

    def close(self):
        self._closed = True
        self.feed_datagram(None, None)
        if self._transport:
            self._transport.close()

    # User methods

    def write(self, data, addr):
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.sendto(data, addr)

    async def read(self):
        if self._closed:
            raise IOError("Enpoint is closed")
        data, addr = await self._queue.get()
        if data is None:
            raise IOError("Enpoint is closed")
        return data, addr

    def abort(self):
        if self._closed:
            raise IOError("Enpoint is closed")
        self._transport.abort()

    # Properties

    @property
    def address(self):
        return self._transport._sock.getsockname()

    @property
    def closed(self):
        return self._closed


class LocalEndpoint(Endpoint):
    pass


class RemoteEndpoint(Endpoint):

    def write(self, data):
        super().write(data, None)

    async def read(self):
        data, addr = await super().read()
        return data


async def open_datagram_endpoint(host='0.0.0.0', port=0, *,
                                 endpoint_factory=Endpoint,
                                 remote=False, loop=None,
                                 **kwargs):
    if loop is None:
        loop = asyncio.get_event_loop()
    kwargs['remote_addr' if remote else 'local_addr'] = host, port
    endpoint = endpoint_factory()
    factory = lambda: DatagramEndpointProtocol(endpoint)
    await loop.create_datagram_endpoint(factory, **kwargs)
    return endpoint


async def open_local_endpoint(host='0.0.0.0', port=0, *,
                              queue_size=None, loop=None, **kwargs):
    endpoint_factory = lambda: LocalEndpoint(queue_size)
    return await open_datagram_endpoint(host, port, remote=False,
                                        endpoint_factory=endpoint_factory,
                                        loop=loop, **kwargs)


async def open_remote_endpoint(host='0.0.0.0', port=0, *,
                               queue_size=None, loop=None, **kwargs):
    endpoint_factory = lambda: RemoteEndpoint(queue_size)
    return await open_datagram_endpoint(host, port, remote=True,
                                        endpoint_factory=endpoint_factory,
                                        loop=loop, **kwargs)


if __name__ == '__main__':

    async def main():
        local = await open_local_endpoint()
        remote = await open_remote_endpoint(*local.address)
        remote.write(b'Hey Hey, My My')
        return await local.read()

    loop = asyncio.get_event_loop()
    data, addr = loop.run_until_complete(main())
    message = "Got {data!r} from {addr[0]} port {addr[1]}"
    print(message.format(data=data.decode(), addr=addr))
