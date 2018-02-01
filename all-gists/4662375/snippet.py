from requests.models import Response

class fixedjson(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, inst, cls):
        result = self.func(inst)

        class proxy(type(result)):
            def __call__(self):
                return self

        if isinstance(result, (dict, int, float, unicode, str, tuple, list)):
            return proxy(result)
        elif result is None:
            return proxy()
        else:
            raise NotImplementedError

        return proxy

Response.json = fixedjson(Response.json)


import requests
x = requests.get('http://httpbin.org/ip')
print repr(x.json)
print repr(x.json())