from concurrent import futures
from tornado import escape, gen, web
from tornado.wsgi import WSGIContainer


class WSGIHandler(web.RequestHandler):
    thread_pool_size = 10

    def initialize(self, wsgi_application):
        self.wsgi_application = wsgi_application

    @web.asynchronous
    @gen.coroutine
    def get(self):
        # based on wsgi.WSGIContainer
        # TODO: handle iterator response
        data = {}
        response = []

        def start_response(status, response_headers, exc_info=None):
            data["status"] = status
            data["headers"] = response_headers
            return response.append
        app_response = yield self.executor.submit(self.wsgi_application,
            WSGIContainer.environ(self.request), start_response)
        response.extend(app_response)
        body = b"".join(response)
        if hasattr(app_response, "close"):
            yield self.executor.submit(app_response.close)
        if not data:
            raise Exception("WSGI app did not call start_response")

        status_code, reason = data["status"].split(None, 1)
        status_code = int(status_code)
        headers = data["headers"]
        body = escape.utf8(body)

        self.set_status(status_code, reason)
        for key, value in headers:
            self.set_header(key, value)
        self.write(body)

    post = put = delete = head = options = get

    @property
    def executor(self):
        cls = type(self)

        if not hasattr(cls, '_executor'):
            cls._executor = futures.ThreadPoolExecutor(cls.thread_pool_size)

        return cls._executor


def test():
    import time

    def simple_app(environ, start_response):
        time.sleep(1)

        status = '200 OK'
        response_headers = [("Content-type", "text/plain")]
        start_response(status, response_headers)
        return ["Hello world!\n"]

    application = web.Application([
        (r'/.*', WSGIHandler, {'wsgi_application': simple_app}),
    ])

    from tornado import ioloop, log
    log.enable_pretty_logging()
    application.listen(8888)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    test()
