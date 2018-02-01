from random import randint
from django.http import HttpResponse

class HTCPCPMiddleware(object):
    """
    This middleware allows a your django project to act as a HTCPCP (Hyper
    Text Coffee Pot Control Protocol) server. If the user requests to BREW
    a coffee, and it is not on the list. Then it will get a `406 Not
    Acceptable`, and randomly it will respond with `418 I'm a teapot`.
    
    If the request is not a HTCPCP (BREW) Request then the middleware will
    quit leaving django to handle the request.
    """
    coffee_list = [
        '/espresso/',
        '/espresso/americano/',
        '/espresso/lungo/',
        '/espresso/flat-white/',
        '/black-coffee/',
        '/latte/',
        '/ristretto/',
        '/cappuccino/'
    ]
    
    def process_request(self, request):
        if request.method != 'BREW' or request.method != 'WHEN':
            return
        
        if randint(-10, 5) > 0:
            return HttpResponse('I\'m a teapot short and stout.', status=418)
        
        if request.method == 'WHEN':
            return HttpResponse('Your coffee is complete.')
        
        if request.path in self.coffee_list:
            return HttpResponse('The coffee is brewed, please send a WHEN request when we should stop pouring the milk.')
        else:
            return HttpResponse('Unrecognised coffee, %s' % ', '.join(self.coffee_list), status=406)
