# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Extended and ported to NDB by Bryan Goldstein.

"""Utility classes and methods for use with simplejson and appengine.

Provides both a specialized simplejson encoder, ModelEncoder, designed to simplify
encoding directly from NDB Models and query results to JSON. A helper function, 
encode, is also provided to further simplify usage.

  ModelEncoder: Adds support for NDB Models to simplejson.
  encode(input): Direct method to encode NDB Model objects as JSON.
"""

import datetime
import simplejson
import time

from google.appengine.api import users
from ndb import model, query


class ModelEncoder(simplejson.JSONEncoder):
  
  """
  Extends JSONEncoder to add support for NDB Models and query results.
  
  Adds support to simplejson JSONEncoders for NDB Models and query results by
  overriding JSONEncoder's default method.
  """
  
  def default(self, obj):
    """Tests the input object, obj, to encode as JSON."""

    if hasattr(obj, 'to_dict'):
      return getattr(obj, 'to_dict')()

    if isinstance(obj, query.Query):
      return list(obj)

    elif isinstance(obj, datetime.datetime):
      return obj.isoformat()

    elif isinstance(obj, time.struct_time):
      return list(obj)

    elif isinstance(obj, users.User):
      output = {}
      methods = ['nickname', 'email', 'auth_domain']
      for method in methods:
        output[method] = getattr(obj, method)()
      return output

    elif isinstance(obj, model.Key):
      return obj.get()

    return simplejson.JSONEncoder.default(self, obj)


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