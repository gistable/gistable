import json
from bson.objectid import ObjectId
from flask import current_app


class MongoEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        else:
            return json.JSONEncoder.default(self, o)


def jsonify(data):
    data = json.dumps(data, cls = MongoEncoder, indent=4, sort_keys=True)
    return current_app.response_class(data, mimetype='application/json')