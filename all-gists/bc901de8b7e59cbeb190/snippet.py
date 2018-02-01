import webapp2
import mimetypes
import os
import time
from datetime import datetime
import base64

_here = os.path.dirname(__file__)

USERNAME = 'foo'
PASSWORD = 'bar'


def check_auth(auth):
  encoded_auth = auth[1]
  username_colon_pass = base64.b64decode(encoded_auth)
  username, password = username_colon_pass.split(':')
  return username == USERNAME and password == PASSWORD


class Handler(webapp2.RequestHandler):

  def get(self, path):
    auth = self.request.authorization
    if auth is None or not check_auth(auth):
      self.response.status_int = 401
      self.response.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
      return
    request_etag = self.request.headers.get('If-None-Match')
    if path.endswith('/') or not path:
      path = path + 'index.html'
    abs_path = os.path.join(_here, path)
    if os.path.isdir(abs_path):
      self.redirect(path + '/')
      return
    mimetype = mimetypes.guess_type(path)[0]
    try:
      stat = os.stat(abs_path)
    except (OSError, IOError):
      self.response.status_int = 404
      self.response.out.write('Not found.')
      return
    time_obj = datetime.fromtimestamp(stat.st_ctime).timetuple()
    headers = {'Content-Type': mimetype or ''}
    headers['Last-Modified'] =  time.strftime('%a, %d %b %Y %H:%M:%S GMT', time_obj)
    headers['ETag'] = '"{}"'.format(headers['Last-Modified'])
    if headers['ETag'] == request_etag:
      self.response.status_int = 304
      return
    fp = open(abs_path)
    self.response.headers.update(headers)
    self.response.out.write(fp.read())


app = webapp2.WSGIApplication([
    ('/(.*)', Handler),
])
