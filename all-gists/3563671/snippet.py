from django.http import HttpResponse
from django.utils import simplejson

def json_response(func):
    
    """
    
    @json_response
    
    A decorator thats takes a view response and turns it into json. If a callback is added
    through GET or POST the response is JSONP.
    
    Example usage:
    
    from django_decorators.decorators import json_response
    @json_response
    def any_view(request):
        return {'this will be': 'JSON'}
    
    Returns a JSON string.
    
    Now, if you need a JSONP response, just add a callback GET or POST variable. :)
    
    ---
    
    https://github.com/julian-amaya/django-decorators
    https://gist.github.com/871954
    https://gist.github.com/1568174
    
    """
    
    def decorator(request, *args, **kwargs):
        objects = func(request, *args, **kwargs)
        if isinstance(objects, HttpResponse):
            return objects
        # Even after using `functools.wraps`, I get:
        # Error: "'dict' object has no attribute 'status_code'".
#         if objects.status_code != 200:
#             return objects
        # It just seems like a good idea to check for a 200 status code... Oh well. :(
        try:
            data = simplejson.dumps(objects)
            if 'callback' in request.REQUEST:
                # A jsonp response!
                data = '%s(%s);' % (request.REQUEST['callback'], data)
                return HttpResponse(data, 'text/javascript; charset=utf-8')
        except:
            data = simplejson.dumps(str(objects))
        return HttpResponse(data, 'application/json; charset=utf-8')
    return decorator