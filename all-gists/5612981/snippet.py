import collections
import json
import redis
import threading
from tornado import gen
from tornado import ioloop
from tornado import web
from tornado.options import define
from tornado.options import options
import tornadoredis
import weakref


define("pubsub_channel", default="tyron_pubsub", help="Redis pub/sub channel")
define("redis_hostname", default="localhost", help="Redis host address")
define("redis_port", default=6379, help="Redis host port")
define("redis_db", default=0, help="Redis host db")
define("webserver_port", default=8080, help="Webserver port")


class RedisSub(threading.Thread):
    """
    subscribes to a redis pubsub channel and routes
    messages to subscribers

    messages have this format
    {'channel': ..., 'data': ...}

    """

    def __init__(self, pubsub_channel, redis_hostname, redis_port, redis_db, redis_password=None):
        threading.Thread.__init__(self)
        self.pubsub_channel = pubsub_channel
        self.redis_hostname = redis_hostname
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password
        self.subscriptions = collections.defaultdict(collections.deque)
        self._init_redis()

    def _init_redis(self):
        self.client = self.get_redis_connection()
        self.pubsub = self.client.pubsub()
        self.pubsub.subscribe(self.pubsub_channel)

    def get_redis_connection(self):
        return redis.Redis(
            self.redis_hostname,
            self.redis_port,
            self.redis_db,
            self.redis_password
        )

    def subscribe(self, channel, callback):
        self.subscriptions[channel].append(callback)

    def decode_message(self, message):
        return json.loads(message)

    def parse_message(self, message):
        msg = self.decode_message(message['data'])
        return msg['channel'], msg['data']

    def notify(self, channel, data):
        while True:
            try:
                cb = self.subscriptions[channel].pop()
            except IndexError:
                break
            if isinstance(cb, (weakref.ref,)):
                cb = cb()
            if cb is not None:
                cb(data)

    def run(self):
        for message in self.pubsub.listen():
            if message['type'] != 'message':
                continue
            self.notify(*self.parse_message(message))

class SubscribeHandler(web.RequestHandler):

    def __call__(self, chunk=None):
        self.finish(chunk)

    @web.asynchronous
    def get(self, channel):
        self.application.pubsub.subscribe(
            channel=channel,
            callback=weakref.ref(self)
        )

    post = get

class RedisStore(web.RequestHandler):

    @web.asynchronous
    @gen.engine
    def get(self, key):
        client = tornadoredis.Client(
            connection_pool=self.application.connection_pool
        )
        value = yield gen.Task(client.get, key)
        self.finish(value)

    post = get

class HealthCheck(web.RequestHandler):

    def get(self, key):
        self.finish('OK')

def start_pubsub_thread():
    pubsub = RedisSub(
        pubsub_channel=options.pubsub_channel,
        redis_hostname=options.redis_hostname,
        redis_port=options.redis_port,
        redis_db=options.redis_db
    )
    pubsub.daemon = True
    pubsub.start()
    return pubsub

def redis_store_connection_pool():
    return tornadoredis.ConnectionPool(
        host=options.redis_hostname,
        port=options.redis_port,
        max_connections=250,
        wait_for_available=True
    )

def main():
    options.parse_command_line()
    application = web.Application([
        (r"/health/", HealthCheck),
        (r"/store/(.*)/", RedisStore),
        (r"/(.*)/", SubscribeHandler),
    ])
    application.pubsub = start_pubsub_thread()
    application.connection_pool = redis_store_connection_pool()
    application.listen(options.webserver_port)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
