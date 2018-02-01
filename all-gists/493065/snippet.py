from json import JSONEncoder
from pymongo.objectid import ObjectId

class MongoEncoder(JSONEncoder):      
    def _iterencode(self, o, markers=None):
        if isinstance(o, ObjectId):
            return """ObjectId("%s")""" % str(o)
        else:
            return JSONEncoder._iterencode(self, o, markers)