from django.core.cache import cache
from django.http import HttpResponseForbidden
from functools import wraps
from django.utils.decorators import available_attrs

def ratelimit(limit=10,length=86400):
    """ The length is in seconds and defaults to a day"""
    def decorator(func):
        def inner(request, *args, **kwargs):
            ip_hash = str(hash(request.META['REMOTE_ADDR']))
            result = cache.get(ip_hash)
            if result:
                result = int(result)
                if result == limit:
                    return HttpResponseForbidden("Ooops too many requests today!")
                else:
                    result +=1
                    cache.set(ip_hash,result,length)
                    return func(request,*args,**kwargs)
            cache.add(ip_hash,1,length)
            return func(request, *args, **kwargs)
        return wraps(func, assigned=available_attrs(func))(inner)
    return decorator