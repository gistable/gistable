#! /usr/bin/python

import asyncio
import os


@asyncio.coroutine
def do_writing(writer):
    for i in range(1, 4):
        writer.write(("stuff " + str(i)).encode())
        yield from asyncio.sleep(1)
    writer.close()


@asyncio.coroutine
def do_reading(reader):
    while not reader.at_eof():
        some_bytes = yield from reader.read(2 ** 16)
        print("here's what we got:", some_bytes)


@asyncio.coroutine
def main():
    read_fd, write_fd = os.pipe()
    reader = asyncio.StreamReader()
    read_protocol = asyncio.StreamReaderProtocol(reader)
    read_transport, _ = yield from loop.connect_read_pipe(
        lambda: read_protocol, os.fdopen(read_fd))
    write_protocol = asyncio.StreamReaderProtocol(asyncio.StreamReader())
    write_transport, _ = yield from loop.connect_write_pipe(
        lambda: write_protocol, os.fdopen(write_fd, 'w'))
    writer = asyncio.StreamWriter(write_transport, write_protocol, None, loop)

    loop.create_task(do_writing(writer))
    yield from do_reading(reader)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()