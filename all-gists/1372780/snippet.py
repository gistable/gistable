import datetime
import simplejson

from pymongo.dbref import DBRef
from pymongo.objectid import ObjectId


class MongoEngineEncoder(simplejson.JSONEncoder):
    """Handles Encoding of ObjectId's"""

    def default(self, obj, **kwargs):

        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, DBRef):
            return {'collection': obj.collection,
                    'id': str(obj.id),
                    'database': obj.database}
        return simplejson.JSONEncoder.default(obj, **kwargs)


class MongoEngineSerializer(object):
    """Wrapper around simplejson that strips whitespace and uses
    MongoEngineEncoder to handle dumping datetimes / ObjectId's and DBRefs
    """

    def loads(self, payload):
        return simplejson.loads(payload)

    def dumps(self, obj, cls=None):
        cls = cls or MongoEngineEncoder
        return simplejson.dumps(obj.to_mongo(), separators=(',', ':'), cls=cls)
