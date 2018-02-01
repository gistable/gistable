import tornado.httpclient
import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
import tornado.gen
import tornado.autoreload
import time, json
import tornado.httpserver


class SomeWork(tornado.web.RequestHandler):
        @tornado.web.asynchronous
        def get(self):
                ioloop = tornado.ioloop.IOLoop.instance()
                ioloop.add_timeout(time.time() + 0.5, self._finish_req)

        def _finish_req(self):
                self.finish()


class Blocking(tornado.web.RequestHandler):
        def get(self):
                req = tornado.httpclient.HTTPRequest("http://127.0.0.1:8888/work")
                client = tornado.httpclient.HTTPClient()
                response = client.fetch(req)

class Async(tornado.web.RequestHandler):
        @tornado.web.asynchronous
        @tornado.gen.engine
        def get(self):
                req = tornado.httpclient.HTTPRequest("http://127.0.0.1:8888/work")
                client = tornado.httpclient.AsyncHTTPClient()
                response = yield tornado.gen.Task(client.fetch, req)
                self.finish()
                
application = tornado.web.Application([
        (r"/async", Async),
        (r"/work", SomeWork),
        (r"/blocking", Blocking)
])


if __name__ == "__main__":
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8888)
        tornado.autoreload.start()
        tornado.ioloop.IOLoop.instance().start()                
