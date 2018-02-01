# -*- coding:utf-8 -*-
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application

class MiddleWare(object):
    def process_request(self, handler):
        pass

    def process_response(self, handler):
        pass


class CheckLogin(MiddleWare):
    def is_login(self, handler):
        pwd = handler.get_argument("pwd", "")
        if not pwd:
            raise Exception("login required")
        else:
            return True

    def process_request(self, handler):
        self.is_login(handler)

session_counter = 0


class Counter(MiddleWare):
    def process_request(self, handler):
        global session_counter
        session_counter = session_counter + 1


class MiddleHandler(RequestHandler):

    def initialize(self, middleware):
        self.middleware = middleware

    def prepare(self):
        for middleware in self.middleware:
            middleware.process_request(self)

    def finish(self, chunk=None):
        super(MiddleHandler, self).finish(chunk)

    def write_error(self, status_code, **kwargs):
        exc_cls, exc_instance, trace = kwargs.get("exc_info")
        if status_code != 200:
            self.set_status(status_code)
            self.write({"msg": str(exc_instance)})


class EchoHandler(MiddleHandler):
    def get(self):
        message = self.get_argument("msg", "world")
        self.write("hello, %s, current online: %d" % (message, session_counter))


def get_middleware():
    return (CheckLogin(), Counter())

if __name__ == '__main__':
    loop = IOLoop.instance()
    middleware_list = get_middleware()
    app = Application([(r"/echo", EchoHandler, dict(middleware=middleware_list))])
    app.listen(8888)
    loop.start()