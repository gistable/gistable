class MongoEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, ObjectId):
            return str(o)
        else:
            return json.JSONEncoder._iterencode(self, o, markers)

def smart_json_response(data):
    data = json.dumps(data, cls = MongoEncoder, indent=4)
    return current_app.response_class(data, mimetype='application/json')
