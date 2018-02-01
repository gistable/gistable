# -*- coding:utf-8 -*-
"""

lib/RedisSessionStore.py
~~~~~~~~~~~~~~

Flask 0.7, session store in redis

ref by https://gist.github.com/994937

:author: linnchord@gmail.com
:date:2011-08-04

:update: change msgpack to cPickle 2011-12-05

"""
import redis, cPickle
from flask import Flask, request, session, json
from werkzeug.contrib.sessions import Session, SessionStore

class RedisSessionStore(SessionStore):

    def __init__(self, key_prefix=None, host='127.0.0.1', port=6379, dbindex=1, expire=1800, password=None):
        SessionStore.__init__(self)

        self.redis = redis.Redis(host, port, dbindex, password=password)
        self.key_prefix = key_prefix
        self.expire = expire

    def save(self,session):
        key = self._get_session_key(session.sid)
        data = cPickle.dumps(dict(session))
        self.redis.setex(key, data, self.expire)

    def delete(self, session):
        key = self._get_session_key(session.sid)
        self.redis.delete(key)

    def get(self, sid):
        key = self._get_session_key(sid)
        data = self.redis.get(key)
        if data:
            self.redis.setex(key, data, self.expire)
            data = cPickle.loads(data)
        else:
            data = {}

        return self.session_class(data, sid, False)


    def _get_session_key(self,sid):
        key = self.key_prefix + sid
        if isinstance(key, unicode):
          key = key.encode('utf-8')
        return key

    
    @staticmethod
    def init_app(app):
        app.session_store = RedisSessionStore(
            app.config['SESSION_KEY_PREFIX'],
            app.config['SESSION_REDIS_HOST'],
            dbindex=app.config['SESSION_REDIS_DB'],
            expire=app.config['SESSION_LIFETIME'],
            password=app.config['REDIS_PASSWORD']
        )
        app.session_key = app.config['SESSION_KEY']
    

class SessionMixin(object):

  __slots__ = ('session_key', 'session_store')

  def open_session(self, request):
    sid = request.cookies.get(self.session_key, None)
    if sid is None:
        return self.session_store.new()
    else:
        return self.session_store.get(sid)

  def save_session(self, session, response):
    if session.should_save:
        self.session_store.save(session)
        response.set_cookie(self.session_key, session.sid)
    return response


class MyFlask(SessionMixin, Flask): pass

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

HOW TO USE

app = MyFlask(__name__)
RedisSessionStore.init_app(app)

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

APP CONFIG:

SESSION_REDIS_HOST = '127.0.0.1'
SESSION_REDIS_PORT = 6379
SESSION_REDIS_DB = 1

SESSION_KEY = '_myapp_sid'
SESSION_KEY_PREFIX = 'session_myapp_'

SESSION_LIFETIME = 900