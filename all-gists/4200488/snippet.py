# Taken from http://taketwoprogramming.blogspot.com/2009/06/subclassing-jsonencoder-and-jsondecoder.html

class DateTimeAwareJSONEncoder(JSONEncoder):
  """ 
  Converts a python object, where datetime and timedelta objects are converted
  into objects that can be decoded using the DateTimeAwareJSONDecoder.
  """
  def default(self, obj):
    if isinstance(obj, datetime):
      return {
        '__type__' : 'datetime',
        'year' : obj.year,
        'month' : obj.month,
        'day' : obj.day,
        'hour' : obj.hour,
        'minute' : obj.minute,
        'second' : obj.second,
        'microsecond' : obj.microsecond,
      }

    elif isinstance(obj, timedelta):
      return {
        '__type__' : 'timedelta',
        'days' : obj.days,
        'seconds' : obj.seconds,
        'microseconds' : obj.microseconds,
      }

    else:
      return JSONEncoder.default(self, obj)

class DateTimeAwareJSONDecoder(JSONDecoder):
  """ 
  Converts a json string, where datetime and timedelta objects were converted
  into objects using the DateTimeAwareJSONEncoder, back into a python object.
  """

  def __init__(self):
      JSONDecoder.__init__(self, object_hook=self.dict_to_object)

  def dict_to_object(self, d):
    if '__type__' not in d:
      return d

    type = d.pop('__type__')
    if type == 'datetime':
      return datetime(**d)
    elif type == 'timedelta':
      return timedelta(**d)
    else:
      # Oops... better put this back together.
      d['__type__'] = type
      return d