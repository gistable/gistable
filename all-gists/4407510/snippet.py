#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from tornado.platform.twisted import TwistedIOLoop
from twisted.internet import reactor
TwistedIOLoop().install()

import tornado.httpserver
import tornado.options
import tornado.web

from tornado.options import define, options

from twisted.internet import defer
from twisted.internet import threads


define("port", default=8888, help="run on the given port", type=int)


def count(n):
    """
    CPU bound function.
    """
    for i in xrange(n):
        pass
    return str(n)


def longCall(n, raise_exception=False):
    """
    imitate long async operation.
    """
    df = defer.Deferred()
    if not raise_exception:
        reactor.callLater(n, df.callback, u'success')
    else:
        reactor.callLater(n, df.errback, u'error occured')
    return df


class MainHandler(tornado.web.RequestHandler):
    """
    Immidiate response.
    """
    def get(self):
        self.write("Hello, world")


class CallLaterHandler(tornado.web.RequestHandler):
    """
    Test Deferred using reactor.callLater
    """
    @tornado.web.asynchronous
    def get(self):
        df = longCall(20)
        df.addCallback(self.on_callback)
        return df

    def on_callback(self, res):
        self.write(res)
        self.finish()


class ThreadHandler(tornado.web.RequestHandler):
    """
    Test deferToThread.
    """
    @tornado.web.asynchronous
    def get(self):
        df = threads.deferToThread(count, 10000000)
        df.addCallback(self.on_callback)
        return df

    def on_callback(self, res):
        self.write(res)
        self.finish()


class InlineCallbacksHandler(tornado.web.RequestHandler):
    """
    Test inlineCallbacks.
    """
    @defer.inlineCallbacks
    @tornado.web.asynchronous
    def get(self):
        response = yield longCall(10)
        self.write(response)
        self.finish()


class ExceptionHandler(tornado.web.RequestHandler):
    """
    Test handling exceptions.
    """
    @tornado.web.asynchronous
    def get(self):
        df = longCall(1, raise_exception=True)
        df.addErrback(self.on_error)
        return df

    def on_error(self, err):
        self.write(err.value)
        self.finish()


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/later", CallLaterHandler),
        (r"/inline", InlineCallbacksHandler),
        (r"/thread", ThreadHandler),
        (r"/exception", ExceptionHandler)
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    # Set up your tornado application as usual using `IOLoop.instance`
    reactor.run()


if __name__ == "__main__":
    main()
