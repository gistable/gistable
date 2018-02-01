from datetime import datetime
from pymongo.connection import Connection

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]

        settings = dict(
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.con = Connection('localhost', 27017)
        self.database = self.con["mongosample"]


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        db=self.application.database

        new_comment = {
            "comment" : "what a nice page",
            "author" : "bobby",
            "time" : datetime.utcnow(),
        }

        db.comments.insert(new_comment)

        comments = db["comments"].find()

        self.write("Hello, world. with mongo")
        for c in comments:
            self.write("<br/>")
            self.write(c["comment"])
            self.write(' - ' + c["author"])
            self.write(' at time: ' + str(c["time"]))


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
    