import re
import simplejson
def camelize(value):
    ret = "".join([w.title() for w in re.split(re.compile("[\W_]*"), value)])
    lower = ret[0].lower()
    return "%s%s" % (lower, ret[1:])

def decamelize(value):
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', value).lower()

def dasherize(value):
    return re.sub(r'_', r'-', decamelize(value))
    
class JsonEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return [o.view() if isinstance(o, Base) else simplejson.JSONEncoder.default(self, o) for o in obj]
        elif isinstance(obj, Base):
            return obj.view()
        else:
            return simplejson.JSONEncoder.default(self, obj)

def json_encode(what):
    return simplejson.dumps(what)
    
def json_decode(json):
    return simplejson.loads(json)