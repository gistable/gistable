from flask import Flask
from flask.json import JSONEncoder
from bson import json_util
from mongoengine.base import BaseDocument
from mongoengine.queryset.base import BaseQuerySet

class MongoEngineJSONEncoder(JSONEncoder):
    def default(self,obj):
        if isinstance(obj,BaseDocument):
            return json_util._json_convert(obj.to_mongo())
        elif isinstance(obj,BaseQuerySet):
            return json_util._json_convert(obj.as_pymongo())
        return JSONEncoder.default(self, obj)

'''
To use:
from mongoengine_jsonencoder import MongoEngineJsonEncoder
app = Flask(__name__)
app.json_encoder = MongoEngineJSONEncoder

Now Flask's jsonify works for Mongoengine querysets, and documents.
'''