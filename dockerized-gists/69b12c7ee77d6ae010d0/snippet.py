from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application

from tornado.web import RequestHandler
from tornado.gen import coroutine, Return


class HelloHandler(RequestHandler):

    @coroutine
    def get(self):
        msg = yield self.task()
        self.write(msg)

    @coroutine
    def task(self):
        raise Return('Hello world!')


class HelloHandlerTest(AsyncHTTPTestCase):
    def get_app(self):
        return Application(
            [(r'/', HelloHandler)],
        )

    @gen_test
    def test_one(self):
        res = yield self.http_client.fetch(self.get_url('/'))
        assert res.error is None, 'error: %s' % str(res.error)


import unittest
unittest.main()
