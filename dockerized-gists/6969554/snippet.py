from functools import wraps
from urlparse import urlparse

def cors(func):
    def add_basic_headers(resp, url):
        resp['Access-Control-Allow-Origin'] = url.scheme + "://" + url.netloc
        resp['Access-Control-Allow-Credentials'] = 'true'
        resp['Access-Control-Allow-Methods'] = 'GET'
        resp['Access-Control-Allow-Headers'] = 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type'


    @wraps(func)
    def inner(request, *args, **kw):
        referer = request.META.get('HTTP_REFERER', None)

        if request.method == "OPTIONS":
            resp = HttpResponse("")
            # 20 days
            resp['Access-Control-Max-Age'] = 1728000
            resp['Content-Type'] = 'text/plain charset=UTF-8'
        else:
            resp = func(request, *args, **kw)

        if referer:
            add_basic_headers(resp, urlparse(referer))

        return resp

    return inner

