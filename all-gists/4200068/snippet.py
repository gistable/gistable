###
### Decorator for view function works very well.
###

def GET(route_name, template):
    def deco(func):
        @view_config(route_name=route_name, request_method='GET',
                     renderer='templates/'+template)
        def fn(request):
            # ... do something here ...
            return func(request)
        fn.__name__ = func.__name__
        fn.__doc__  = func.__doc__
        return fn
    return deco


@GET('hello', 'hello.pt')
def hello_view(request):
    return {'title': u'Hello!'}


###
### But decorator for method does not work (results in 404 Not Found).
### Why? Due to Venusian?
###

def GET(route_name, template):
    def deco(func):
        @view_config(route_name=route_name, request_method='GET',
                     renderer='templates/'+template)
        def fn(self):
            # ... do something here ...
            return func(self)
        fn.__name__ = func.__name__
        fn.__doc__  = func.__doc__
        return fn
    return deco


class HelloView(object):

    def __init__(self, request):
        self.request = request

    #@view_config(route_name='hello', renderer='templates/hello.pt')
    @GET('hello', 'hello.pt')
    def hello(self):
        return {'title': 'Hello!'}
