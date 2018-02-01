#!/usr/bin/env python

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPResponse

import mock
import StringIO

def setup_fetch(fetch_mock, status_code, body=None):
    def side_effect(request, **kwargs):
        if request is not HTTPRequest:
            request = HTTPRequest(request)
        buffer = StringIO.StringIO(body)
        response = HTTPResponse(request, status_code, None, buffer)
        future = Future()
        future.set_result(response)
        return future

    fetch_mock.side_effect = side_effect

@gen.coroutine
def main():
    client = AsyncHTTPClient()
    with mock.patch.object(client, 'fetch') as fetch_mock:
        setup_fetch(fetch_mock, 200, 'hello')
        response = yield client.fetch('http://google.com')
        print response.body

IOLoop.instance().run_sync(main)
