import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httputil
import json

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        # do something useful
        name = self.get_argument('foo')
        self.write("Hello, %s" % name)

class TestJSONHandler(tornado.httpserver.HTTPParseBody):

    def __call__(self):
        self.stream.read_bytes(self.content_length, self.parse_json)

    def parse_json(self, data):
        print data
        try:
            json_data = json.loads(data)
        except ValueError:
            raise tornado.httpserver._BadRequestException(
                "Invalid JSON structure."
            )
        if type(json_data) != dict:
            raise tornado.httpserver._BadRequestException(
                "We only accept key value objects!"
            )
        for key, value in json_data.iteritems():
            self.request.arguments[key] = [value,]
        self.done()

application = tornado.web.Application([
    (r"/", MainHandler),
])

body_handlers = [
    ("application/json", TestJSONHandler),
]

if __name__ == "__main__":
    application.listen(8888, body_handlers=body_handlers)
    tornado.ioloop.IOLoop.instance().start()


# USAGE:
# curl -v http://localhost:8888/ -X POST --data-binary '{"foo": "bar"}' -H "Content-type: application/json"
