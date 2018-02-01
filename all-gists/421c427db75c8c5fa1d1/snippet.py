"""A simple demonstration of running background tasks with Tornado.

Here I am using a basic TCP server which handles streams and keeps
them open while asynchronously performing a fake task in the
background. In order to test it, simply telnet to localhost port 8080
and start typing things to see that the server receives the messages.

The advantage to running on an executor instead of conventional
threads is that we can more easily shut it down by stopping the
tornado IO loop.

This demo is partially inspired by the gist that can be found
here__.

__ https://gist.github.com/methane/2185380

"""

from __future__ import print_function
import time
import signal
from random import random, randint
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent import futures
from tornado.tcpserver import TCPServer

class Server(TCPServer):
    """Server for demonstration of running background tasks with
    futures.

    """
    executor = futures.ThreadPoolExecutor(max_workers=1)
    task_complete = False
    clients = set()

    @run_on_executor
    def task(self):
        """Dummy task."""
        time.sleep(random()*randint(0, 5))
        print("Task complete: " + str(randint(0, 9999)))
        IOLoop.instance().add_callback(self.task)
    
    @gen.coroutine
    def handle_stream(self, stream, address):
        print("New connection.")
        Server.clients.add(stream)
        while True:
            try:
                incoming = yield stream.read_until('\n')
                print('Incoming message: ' + incoming)
            except StreamClosedError:
                print("client left.")
                Server.clients.remove(stream)
                break

    @classmethod
    def shutdown(self):
        """Close all open connections."""
        print('shutting down')
        for client in Server.clients:
            if not client.closed():
                client.close()
            Server.clients.remove(client)

if __name__ == "__main__":
    server = Server()
    ioloop = IOLoop.instance()
    ioloop.add_callback(server.task)
    server.listen(8080)
    def shutdown():
        server.shutdown()
        ioloop.stop()
    signal.signal(signal.SIGINT, lambda sig, frame: shutdown())
    ioloop.start()