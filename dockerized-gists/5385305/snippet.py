import json
from shapely.geometry.base import BaseGeometry
from shapely.geometry import shape, mapping

class ShapelyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseGeometry):
            return mapping(obj)
        return json.JSONEncoder.default(self, obj)

class ShapelyDecoder(json.JSONDecoder):
    def decode(self, json_string):
    
        def shapely_object_hook(obj):
            if 'coordinates' in obj and 'type' in obj:
                return shape(obj)
            return obj
        
        return json.loads(json_string, object_hook=shapely_object_hook)

def export_to_JSON(data):
    return json.dumps(data, indent=4, sort_keys=True, cls=ShapelyEncoder)

def load_from_JSON(json_string):
    return json.loads(json_string, cls=ShapelyDecoder)