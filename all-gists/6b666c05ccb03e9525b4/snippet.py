# -*- coding: utf-8 -*-
import asyncio
import re

import asyncio_redis
import tornado.concurrent
import tornado.httpclient
import tornado.web
import tornado.platform.asyncio


def coroutine(func):
    func = asyncio.coroutine(func)

    def decorator(*args, **kwargs):
        future = tornado.concurrent.Future()

        def future_done(f):
            try:
                future.set_result(f.result())
            except Exception as e:
                future.set_exception(e)

        asyncio.async(func(*args, **kwargs)).add_done_callback(future_done)
        return future
    return decorator


class MainHandler(tornado.web.RequestHandler):

    def initialize(self, redis):
        self.redis = redis

    @asyncio.coroutine
    def _get_dolar(self):
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield from tornado.platform.asyncio.to_asyncio_future(
            client.fetch('http://dolarhoje.com')
        )

        dolar = re.search(
            r'<input type="text" id="nacional" value="(?P<dolar>[^"]+)"/>',
            resp.body.decode('utf-8')
        )
        if dolar:
            return dolar.group(1)

    @coroutine
    def get(self):
        dolar = yield from self.redis.get('dolar')
        if not dolar:
            dolar = yield from self._get_dolar()
            yield from self.redis.set('dolar', dolar, expire=60)

        self.write(dolar)


@asyncio.coroutine
def get_redis_connection():
    return (yield from asyncio_redis.Connection.create(
        host='localhost', port=6379
    ))


if __name__ == '__main__':
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    ioloop = asyncio.get_event_loop()

    redis = ioloop.run_until_complete(get_redis_connection())

    app = tornado.web.Application([
        (r"/", MainHandler, dict(redis=redis)),
    ])

    app.listen(8888)
    ioloop.run_forever()