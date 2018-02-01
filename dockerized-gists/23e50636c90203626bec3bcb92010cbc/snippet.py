from datetime import datetime

SUNDAY = 6

class UncleVernonMiddleware(object):
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'].lower() == 'post' and datetime.now().weekday() == SUNDAY:
            start_response('405 METHOD NOT ALLOWED', [])
            return ['No Post On Sundays']
        return self.app(environ, start_response)