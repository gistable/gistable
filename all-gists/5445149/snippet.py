import json
from rest_framework import serializers

class JSONField(serializers.WritableField):
    
    def to_native(self, obj):
        return json.dumps(obj)
    
    def from_native(self, value):
        return json.loads(value)