# -*- coding: utf-8 -*-
from random import randint

import tornado.concurrent
import tornado.platform.asyncio
import tornado.web

from aiopg.sa import create_engine as aiopg_create_engine
import asyncio

from models import user


def asyncio_coroutine(func):
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


class BaseHandler(tornado.web.RequestHandler):
    def _get_engine(self):
        engine = yield from aiopg_create_engine(user='postgres',
                                                database='tornado_chat',
                                                host='127.0.0.1',
                                                password='postgres')
        return engine

    @asyncio.coroutine
    def select(self, table_object):
        engine = yield from self._get_engine()
        with (yield from engine) as conn:
            data = yield from conn.execute(table_object)
        return data

    @asyncio.coroutine
    def insert(self, table_object):
        engine = yield from self._get_engine()
        with (yield from engine) as conn:
            yield from conn.execute(table_object)


class MainHandler(BaseHandler):
    @asyncio_coroutine
    def get(self):
        s = randint(0, 7)
        # print("in  ", '-' * int(s), s)
        # yield from asyncio.sleep(s)
        # print('out ', '-' * int(s), s)

        db_messages = yield from self.select(user.select())
        db_messages = [{"id": i[0], "name": i[1]} for i in db_messages]
        r = yield from self.insert(user.insert().values(name=str(s)))

        if len(db_messages) > 10:
            yield from self.insert(user.delete())
        self.render('index.html', messages=db_messages)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = (
            (r'/', MainHandler),
        )

        tornado.web.Application.__init__(self, handlers)


application = Application()

if __name__ == '__main__':
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    application.listen(8001)
    asyncio.get_event_loop().run_forever()
