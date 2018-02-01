class StaticFactory(object):
    def __init__(self, request):
        request.is_static_asset = True

config.add_static_view('static', static_pkg, factory=StaticFactory)
config.add_request_method(lambda r: False, 'is_static_asset', reify=True)

_default_vary = set([
    'Cookie',
    'Accept',
    'Accept-Language',
    'Authorization',
])

_default_static_vary = set([
    'Accept',
    'Accept-Language',
])

def new_response_subscriber(event):
    request = event.request
    response = event.response

    if request.is_static_asset:
        vary = _default_static_vary
    else:
        vary = _default_vary

    if response.vary is not None:
        response.vary = vary.union(response.vary)
    else:
        response.vary = vary
        
config.add_subscriber(new_response_subscriber, 'pyramid.events.NewResponse')