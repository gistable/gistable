import socket
from tornado.concurrent import TracebackFuture, return_future
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.netutil import bind_unix_socket, Resolver
from tornado.web import RequestHandler, Application

class HelloHandler(RequestHandler):
    def get(self):
        self.write('hello')

SOCKPATH = '/tmp/test.sock'

class UnixResolver(Resolver):
    def initialize(self, resolver):
        self.resolver = resolver

    def close(self):
        self.resolver.close()

    @gen.coroutine
    def resolve(self, host, port, *args, **kwargs):
        if host == 'unixsocket':
            raise gen.Return([(socket.AF_UNIX, SOCKPATH)])
        result = yield self.resolver.resolve(host, port, *args, **kwargs)
        raise gen.Return(result)

@gen.coroutine
def main():
    app = Application([('/', HelloHandler)])
    server = HTTPServer(app)
    server.add_socket(bind_unix_socket(SOCKPATH))

    resolver = UnixResolver(resolver=Resolver())
    AsyncHTTPClient.configure(None, resolver=resolver)

    response = yield AsyncHTTPClient().fetch('http://unixsocket/')
    print response.body

IOLoop.current().run_sync(main)
