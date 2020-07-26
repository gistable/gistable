"""Demo of streaming requests with Tornado.

This script features a client using AsyncHTTPClient's body_producer
feature to slowly produce a large request body, and two server
handlers to receive this body (one is a proxy that forwards to the
other, also using body_producer).

It also demonstrates flow control: if --client_delay is smaller than
--server_delay, the client will eventually be suspended to allow the
server to catch up. You can see this in the logs, as the "client
writing" lines are initially once a second but eventually become less
frequent (the details are platform-dependent and adjustable with
setsockopt, but with the defaults on my Mac the delays start to show
up around chunk 18).

Tested with Python 3.4, Tornado 4.1.dev1 (main branch from 11 Jan 2015),
and Toro 0.7.
Runs on Tornado 4.0 and higher, but 4.0 has a bug with flow control on
kqueue platforms (Mac and BSD) so to see the flow control effects on
those platforms you'll need latest source from github (until 4.1 is released).

"""
import logging
import toro

from tornado.concurrent import Future
from tornado.escape import utf8
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.options import parse_command_line, define, options
from tornado.web import Application, RequestHandler, stream_request_body

define('port', default=8888)
define('debug', default=True)

define('server_delay', default=2.0)
define('client_delay', default=1.0)
define('num_chunks', default=40)

@stream_request_body
class UploadHandler(RequestHandler):
    def prepare(self):
        logging.info('UploadHandler.prepare')

    @gen.coroutine
    def data_received(self, chunk):
        logging.info('UploadHandler.data_received(%d bytes: %r)',
                     len(chunk), chunk[:9])
        yield gen.Task(IOLoop.current().call_later, options.server_delay)

    def put(self):
        logging.info('UploadHandler.put')
        self.write('ok')

@stream_request_body
class ProxyHandler(RequestHandler):
    def prepare(self):
        logging.info('ProxyHandler.prepare')
        self.chunks = toro.Queue(1)
        self.fetch_future = AsyncHTTPClient().fetch(
            'http://localhost:%d/upload' % options.port,
            method='PUT',
            body_producer=self.body_producer,
            request_timeout=3600.0)

    @gen.coroutine
    def body_producer(self, write):
        while True:
            chunk = yield self.chunks.get()
            if chunk is None:
                return
            yield write(chunk)

    @gen.coroutine
    def data_received(self, chunk):
        logging.info('ProxyHandler.data_received(%d bytes: %r)',
                     len(chunk), chunk[:9])
        yield self.chunks.put(chunk)

    @gen.coroutine
    def put(self):
        logging.info('ProxyHandler.put')
        # Write None to the chunk queue to signal body_producer to exit,
        # then wait for the request to finish.
        yield self.chunks.put(None)
        response = yield self.fetch_future
        self.set_status(response.code)
        self.write(response.body)

@gen.coroutine
def client():
    @gen.coroutine
    def body_producer(write):
        for i in range(options.num_chunks):
            yield gen.Task(IOLoop.current().call_later, options.client_delay)
            chunk = ('chunk %02d ' % i) * 10000
            logging.info('client writing %d bytes: %r', len(chunk), chunk[:9])
            yield write(utf8(chunk))

    response = yield AsyncHTTPClient().fetch(
        'http://localhost:%d/proxy' % options.port,
        method='PUT',
        body_producer=body_producer,
        request_timeout=3600.0)
    logging.info('client finished with response %d: %r',
                 response.code, response.body)

def main():
    parse_command_line()
    app = Application([
        ('/upload', UploadHandler),
        ('/proxy', ProxyHandler),
    ], debug=options.debug)
    app.listen(options.port)
    IOLoop.instance().spawn_callback(client)
    IOLoop.instance().start()

if __name__ == '__main__':
    main()
