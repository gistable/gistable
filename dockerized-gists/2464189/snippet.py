import json
from decimal import Decimal
from datetime import datetime

# FIXME in pyramid 1.4 this is easier

class JSONRenderer(object):

    ENCODERS = {}

    @classmethod
    def register_encoder(cls, value_class, encoder):
        cls.ENCODERS = {value_class: encoder}

    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')

        if request is not None:
            response = request.response
            ct = response.content_type
            
            if ct == response.default_content_type:
                response.content_type = 'application/json'

        return self.dumps(value)

    def encode(self, value):
        if hasattr(value, '__json__'):
            return value.__json__()

        for value_class, encoder in self.ENCODERS.items():
            if isinstance(value, value_class):
                return encoder(value)

        raise TypeError('%s is not JSON serializable' % value)

    def dumps(self, value):
        return json.dumps(value, default=self.encode)

# FIXME test.  does this need a thunk?
def add_json_encoder(func, cls):
    '''
    A decorator to register encoders

    @add_json_encoder(Foo)
    def encode_foo(value):
        return value.dump()
    '''
    
    JSONRenderer.register_encoder(cls, func)
    return func

JSONRenderer.register_encoder(set, list)
JSONRenderer.register_encoder(datetime, lambda value: value.isoformat())
JSONRenderer.register_encoder(Decimal, lambda value: str(value))

try:
    from athanor import EnumSymbol
    JSONRenderer.register_encoder(EnumSymbol, lambda value: value.name)
except:
    pass

try:
    from formencode import Invalid
    JSONRenderer.register_encoder(Invalid, lambda value: value.unpack_errors())
except:
    pass
