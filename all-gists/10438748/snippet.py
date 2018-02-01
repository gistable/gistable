# -*- coding: utf-8 -*-
import webapp2
from model import *
from google.appengine.api import memcache
import hashlib
import logging
import random
import string

import json
import datetime
import time
import email.utils
#from google.appengine.api import users
#from ndb import model, query
 
def auth_required(handler):
  """Requires that a user be logged in to access the resource"""
  def check_login(self, *args, **kwargs):
      return handler(self, *args, **kwargs)
  return check_login

#https://gist.github.com/brysgo/1572547
class ModelEncoder(json.JSONEncoder):
  """ 
  Extends JSONEncoder to add support for NDB Models and query results.
  
  Adds support to simplejson JSONEncoders for NDB Models and query results by
  overriding JSONEncoder's default method.
  """
  def default(self, obj):
    """Tests the input object, obj, to encode as JSON."""
    if hasattr(obj, 'to_dict'):
      return getattr(obj, 'to_dict')()
    if isinstance(obj, ndb.query.Query):
      return list(obj)
    elif isinstance(obj, datetime.datetime):
      return obj.isoformat()
    elif isinstance(obj, time.struct_time):
      return list(obj)
    elif isinstance(obj, ndb.model.Key):
      return obj.get()
 
    return json.JSONEncoder.default(self, obj)
 
def encode(input):
  """ 
  Encode an input Model object as JSON
    Args:
      input: A Model object or DB property.
    Returns:
      A JSON string based on the input object. 
    Raises:
      TypeError: Typically occurs when an input object contains an unsupported
        type.
  """
  return ModelEncoder().encode(input)

class MemcacheHolder:
  def __init__(self,etag,last_modified,data):
    self.etag = etag
    self.last_modified = last_modified
    self.data = data

class RestHandler(webapp2.RequestHandler):
  def get_etag(self):
    request_etag = None
    if 'If-None-Match' in self.request.headers:
      request_etag = self.request.headers['If-None-Match']
      if request_etag.startswith('"') and request_etag.endswith('"'):
        request_etag = request_etag[1:-1]
    return request_etag

  def get_last_modified(self):
    if 'If-Modified-Since' in self.request.headers:
      text = self.request.headers['If-Modified-Since']
      return datetime.datetime(*email.utils.parsedate(text)[:6])
    return None

  # Wed, 22 Oct 2008 10:52:40 GMT
  def time_to_rfc1123(self, target):
    stamp = time.mktime(target.timetuple())
    return email.utils.formatdate(timeval=stamp, localtime=False, usegmt=True)

  def response_json(self, encoded):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(encoded)

  def response_object(self, obj):
    self.response_json(encode(obj))

  def response_error(self, status, status_message, code, message, errors):
    self.response.status_int = status
    self.response.status_message = status_message
    self.response.status = str(status) + status_message

    obj = { 'code': code,
            'message': message,
            'errors' : errors
          }
    self.response_object(obj)

  def response_bad_request(self, code, message, errors):
    self.response_error(400, "Bad Request", code, message, errors)
  def response_unauthorized(self, code, message, errors):
    self.response_error(401, "Unauthorized", code, message, errors)
  def response_forbidden(self, code, message, errors):
    self.response_error(403, "Forbidden", code, message, errors)
  def response_not_found(self, code, message, errors):
    self.response_error(404, "Not Found", code, message, errors)
  def response_not_modified(self, etag, last_modified):
    if etag:
      self.response.headers["Etag"] = etag
      #self.response.etag = etag
    if last_modified:
      self.response.headers["Last-Modified"] = self.time_to_rfc1123(last_modified)
    self.response.status_int = 304
    self.response.status_message = "Not Modified"
    self.response.status = "304 Not Modified"

class MyApiHandler(RestHandler):
  @auth_required
  def get(self):
    self.response.headers["Cache-Control"] = "must-revalidate, max-age=0"

    holder = memcache.get('mymodel_all')
    if holder is None:
      models = MyModel.query().order(MyNodel.updated).fetch()
      data = encode(models)
      etag = hashlib.md5(data).hexdigest()
      last_modified = models[0].updated if len(models) > 0 else datetime.datetime.now()
      holder = MemcacheHolder(etag, last_modified, data)
      memcache.add('mymodel_all', holder)

    # validate last-modified : if-modified-since
    request_last = self.get_last_modified()
    if request_last is not None:
      if holder.last_modified - request_last < datetime.timedelta(seconds=1):
        return self.response_not_modified(etag=holder.etag,
                                    last_modified=holder.last_modified)

    # validate the etag : if-none-match
    request_etag = self.get_etag()
    if request_etag is not None:
      if request_etag == holder.etag: #matched
        return self.response_not_modified(etag=holder.etag,
                                    last_modified=holder.last_modified)

    self.response_json(holder.data)
    #self.response.md5_etag()
    self.response.headers["Etag"] = holder.etag
    self.response.headers["Last-Modified"] = self.time_to_rfc1123(holder.last_modified)
