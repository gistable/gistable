
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash
from werkzeug.contrib.sessions import Session, SessionStore
from cPickle import HIGHEST_PROTOCOL
from random import random
from flask import json
class MemcachedSessionStore(SessionStore):

  def __init__(self, servers=None, key_prefix=None, default_timeout=300):
    SessionStore.__init__(self)


    if isinstance(servers, (list, tuple)):
      try:
      	import cmemcache as memcache
      	is_cmemcache = True
      except ImportError:
        try:
        	import memcache 
        	is_cmemcache = False
        	is_pylibmc = False
        except ImprotError:
          try:
          	import pylibmc as memcache
          	is_cmemcache = False
          	is_pylibmc = True
          except ImportError:
          	raise RuntimeErorr(' no memcache module found ')

      if is_cmemcache:
      	client = memcache.Client(map(str, servers))
        try:
          client.debuglog = lambda *a: None
        except Exception:
        	pass
      else:
        if is_pylibmc:
        	client = memcache.Client(servers, False)
        else:
        	client = memcache.Client(servers, False, HIGHEST_PROTOCOL)
    else:
    	client = servers

    self._memcache_client = client
    self._memcache_key_prefix = key_prefix
    self._memcache_timeout = default_timeout

  def save(self, session):
    key = self._get_memcache_key(session.sid)
    data = json.dumps(dict(session))
    print "{0}:{1}".format(key, data)
    self._memcache_client.set( key, data )

  def delete(self, session):
    key = self._get_memcache_key(session.sid)
    self._memcache_client.delete(key)

  def get(self, sid):
    key = self._get_memcache_key(sid)
    data = self._memcache_client.get( key )
    if data is not None:
    	data = json.loads(data)
    else:
    	data = {}
    return self.session_class( data, sid, False)

  def _get_memcache_key(self, sid):
    key = self._memcache_key_prefix + sid
    if isinstance(key, unicode):
      key = key.encode('utf-8')
    return key 

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


class MyFlask( SessionMixin, Flask): pass


app = MyFlask(__name__)
app.session_key = '_sess_myflask'
app.session_store = MemcachedSessionStore(['127.0.0.1:1122'], 'myflask:')

@app.route('/a')
def a():
	session['a'] = 'from a {0}'.format(random())
	return u'''<!doctype html>
	<html>
    <head>
      <title>Hello Test</title>
    </head>
	  <body>
	    <h1>saved {0}</h1>
	  </body>
	</html>'''.format( session['a'] )

@app.route('/b')
def b():
  return u'''<!doctype html>
    <html>
      <head>
        <title>Hello Test</title>
      </head>
      <body>
        <h1>loaded {0}</h1>
      </body>
    </html>'''.format( session['a'] )

if __name__ == '__main__':
	app.run(debug=True)