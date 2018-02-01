import json, datetime

class RoundTripEncoder(json.JSONEncoder):
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return {
                "_type": "datetime",
                "value": obj.strftime("%s %s" % (
                    self.DATE_FORMAT, self.TIME_FORMAT
                ))
            }
        return super(RoundTripEncoder, self).default(obj)

data = {
    "name": "Silent Bob",
    "dt": datetime.datetime(2013, 11, 11, 10, 40, 32)
}

print json.dumps(data, cls=RoundTripEncoder, indent=2)

import json, datetime
from dateutil import parser

class RoundTripDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        type = obj['_type']
        if type == 'datetime':
            return parser.parse(obj['value'])
        return obj

print json.loads(s, cls=RoundTripDecoder)

