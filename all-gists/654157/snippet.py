# NOTE:  This code was extracted from a larger class and has not been
# tested in this form.  Caveat emptor.
import django.conf
import django.contrib.auth
import django.core.handlers.wsgi
import django.db
import django.utils.importlib
import httplib
import json
import logging
import tornado.options
import tornado.template as template
import tornado.web
import traceback

from tornado.options import options, define

class BaseHandler(tornado.web.RequestHandler):
  def prepare(self):
    super(BaseHandler, self).prepare()
    # Prepare ORM connections
    django.db.connection.queries = []

  def finish(self, chunk = None):
    super(BaseHandler, self).finish(chunk = chunk)
    # Clean up django ORM connections
    django.db.connection.close()
    if options.debug:
      logging.info('%d sql queries' % len(django.db.connection.queries))
      for query in django.db.connection.queries:
        logging.debug('%s [%s seconds]' % (query['sql'], query['time']))

    # Clean up after python-memcached
    from django.core.cache import cache
    if hasattr(cache, 'close'):
      cache.close()

  def get_django_session(self):
    if not hasattr(self, '_session'):
      engine = django.utils.importlib.import_module(
        django.conf.settings.SESSION_ENGINE)
      session_key = self.get_cookie(django.conf.settings.SESSION_COOKIE_NAME)
      self._session = engine.SessionStore(session_key)
    return self._session

  def get_user_locale(self):
    # locale.get will use the first non-empty argument that matches a
    # supported language.
    return tornado.locale.get(
      self.get_argument('lang', None),
      self.get_django_session().get('django_language', None),
      self.get_cookie('django_language', None))

  def get_current_user(self):
    # get_user needs a django request object, but only looks at the session
    class Dummy(object): pass
    django_request = Dummy()
    django_request.session = self.get_django_session()
    user = django.contrib.auth.get_user(django_request)
    if user.is_authenticated():
      return user
    else:
      # try basic auth
      if not self.request.headers.has_key('Authorization'):
        return None
      kind, data = self.request.headers['Authorization'].split(' ')
      if kind != 'Basic':
        return None
      (username, _, password) = data.decode('base64').partition(':')
      user = django.contrib.auth.authenticate(username = username,
                                              password = password)
      if user is not None and user.is_authenticated():
        return user
      return None

  def get_django_request(self):
    request = django.core.handlers.wsgi.WSGIRequest(
      tornado.wsgi.WSGIContainer.environ(self.request))
    request.session = self.get_django_session()

    if self.current_user:
      request.user = self.current_user
    else:
      request.user = django.contrib.auth.models.AnonymousUser()

    return request
