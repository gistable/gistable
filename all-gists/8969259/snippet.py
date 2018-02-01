#!/usr/bin/env python
"""
JSON encoder/decoder adapted for use with Google App Engine NDB.

Usage:

  import ndb_json
  
  # Serialize an ndb.Query into an array of JSON objects.
  query = models.MyModel.query()
  query_json = ndb_json.dumps(query)
  
  # Convert into a list of Python dictionaries.
  query_dicts = ndb_json.loads(query_json)
  
  # Serialize an ndb.Model instance into a JSON object.
  entity = query.get()
  entity_json = ndb_json.dumps(entity)
  
  # Convert into a Python dictionary.
  entity_dict = ndb_json.loads(entity_json)


Dependencies:

  - dateutil: https://pypi.python.org/pypi/python-dateutil
"""
 
__author__ = 'Eric Higgins'
__copyright__ = 'Copyright 2013, Eric Higgins'
__version__ = '0.0.5'
__email__ = 'erichiggins@gmail.com'
__status__ = 'Development'


import base64
import datetime
import json
import re
import time
import types

import dateutil.parser
from google.appengine.ext import ndb


def encode_model(obj):
  """Encode objects like ndb.Model which have a `.to_dict()` method."""
  obj_dict = obj.to_dict()
  for key, val in obj_dict.iteritems():
    if isinstance(val, types.StringType):
      try:
        unicode(val)
      except UnicodeDecodeError:
        # Encode binary strings (blobs) to base64.
        obj_dict[key] = base64.b64encode(val)
  return obj_dict


def encode_generator(obj):
  """Encode generator-like objects, such as ndb.Query."""
  return list(obj)


def encode_key(obj):
  """Get the Entity from the ndb.Key for further encoding."""
  # Note(eric): Potentially poor performance for Models w/ many KeyProperty properties.
  return obj.get_async()
  # Alternative 1: Convert into pairs.
  # return obj.pairs()
  # Alternative 2: Convert into URL-safe base64-encoded string.
  # return obj.urlsafe()


def encode_future(obj):
  """Encode an ndb.Future instance."""
  return obj.get_result()


def encode_datetime(obj):
  """Encode a datetime.datetime or datetime.date object as an ISO 8601 format string."""
  # Reformat the date slightly for better JS compatibility.
  # Offset-naive dates need 'Z' appended for JS.
  # datetime.date objects don't have or need tzinfo, so don't append 'Z'.
  zone = '' if getattr(obj, 'tzinfo', True) else 'Z'
  return obj.isoformat() + zone


def encode_complex(obj):
  """Convert a complex number object into a list containing the real and imaginary values."""
  return [obj.real, obj.imag]


def encode_basevalue(obj):
  """Retrieve the actual value from a ndb.model._BaseValue.
  
  This is a convenience function to assist with the following issue:
  https://code.google.com/p/appengine-ndb-experiment/issues/detail?id=208
  """
  return obj.b_val


NDB_TYPE_ENCODING = {
  ndb.MetaModel: encode_model,
  ndb.Query: encode_generator,
  ndb.QueryIterator: encode_generator,
  ndb.Key: encode_key,
  ndb.Future: encode_future,
  datetime.date: encode_datetime,
  datetime.datetime: encode_datetime,
  time.struct_time: encode_generator,
  types.ComplexType: encode_complex,
  ndb.model._BaseValue: encode_basevalue,
  
}


class NdbEncoder(json.JSONEncoder):
  """Extend the JSON encoder to add support for NDB Models."""

  def default(self, obj):
    """Overriding the default JSONEncoder.default for NDB support."""

    obj_type = type(obj)
    # NDB Models return a repr to calls from type().
    if obj_type not in NDB_TYPE_ENCODING and hasattr(obj, '__metaclass__'):
      obj_type = obj.__metaclass__
    fn = NDB_TYPE_ENCODING.get(obj_type)
    if fn:
      return fn(obj)

    return json.JSONEncoder.default(self, obj)


def dumps(ndb_model, **kwargs):
  """Custom json dumps using the custom encoder above."""
  return NdbEncoder(**kwargs).encode(ndb_model)


def dump(ndb_model, fp, **kwargs):
  """Custom json dump using the custom encoder above."""
  for chunk in NdbEncoder(**kwargs).iterencode(ndb_model):
    fp.write(chunk)


def loads(json_str, **kwargs):
  """Custom json loads function that converts datetime strings."""
  json_dict = json.loads(json_str, **kwargs)
  if isinstance(json_dict, list):
    return map(iteritems, json_dict)
  return iteritems(json_dict)


def iteritems(json_dict):
  """Loop over a json dict and try to convert strings to datetime."""
  for key, val in json_dict.iteritems():
    if isinstance(val, dict):
      iteritems(val)
    # Its a little hacky to check for specific chars, but avoids integers.
    elif isinstance(val, basestring) and 'T' in val:
      try:
        json_dict[key] = dateutil.parser.parse(val)
        # Check for UTC.
        if val.endswith(('+00:00', '-00:00', 'Z')):
          # Then remove tzinfo for gae, which is offset-naive.
          json_dict[key] = json_dict[key].replace(tzinfo=None)
      except (TypeError, ValueError):
        pass
  return json_dict
  