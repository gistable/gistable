import logging
import tornado.escape
import tornado.ioloop
import tornado.websocket
import os.path
import uuid

#class MainHandler(tornado.web.RequestHandler):
#    def get(self):
#        self.render("index.html", messages=ChatSocketHandler.cache)

class SocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            }
        chat["html"] = self.render_string("message.html", message=chat)
        self.write_message("omg")
        ChatSocketHandler.update_cache(chat)
        ChatSocketHandler.send_updates(chat)


from flask import Flask

app=Flask(__name__)

@app.route('/')
def index():
    return "ok"


import time
import tornado.web
from tornado.websocket import WebSocketHandler
from tornado.ioloop import PeriodicCallback,IOLoop
import tornado.wsgi

wsgi_app=tornado.wsgi.WSGIContainer(app)

application=tornado.web.Application([
    (r'/websocket', SocketHandler),
    (r'.*',tornado.web.FallbackHandler, {'fallback':wsgi_app })
])

#PeriodicCallback(NowHandler.echo_now,1000).start()

application.listen(2013)
IOLoop.instance().start()