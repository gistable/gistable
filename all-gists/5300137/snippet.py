#!/usr/bin/env python

# An example of decoding/encoding datetime values in JSON data in Python.
# Code adapted from: http://broadcast.oreilly.com/2009/05/pymotw-json.html


from datetime import datetime
import json
from json import JSONDecoder
from json import JSONEncoder

obj = {'name':'foo', 'type': 'bar','date':datetime.now()}


class DateTimeDecoder(json.JSONDecoder):

    def __init__(self, *args, **kargs):
        JSONDecoder.__init__(self, object_hook=self.dict_to_object,
                             *args, **kargs)
    
    def dict_to_object(self, d): 
        if '__type__' not in d:
            return d

        type = d.pop('__type__')
        try:
            dateobj = datetime(**d)
            return dateobj
        except:
            d['__type__'] = type
            return d

class DateTimeEncoder(JSONEncoder):
    """ Instead of letting the default encoder convert datetime to string,
        convert datetime objects into a dict, which can be decoded by the
        DateTimeDecoder
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
        else:
            return JSONEncoder.default(self, obj)

            
j = json.loads(json.dumps(obj,cls=DateTimeEncoder), cls=DateTimeDecoder)
print j['date']
print type(j['date'])
