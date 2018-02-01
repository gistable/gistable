def customized(default=None, template=None):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kargs):
            self.template = default
            if self.current_user:
                self.template = template
            return method(self, *args, **kargs)
        return wrapper
    return decorator

# Usage example:

class MainHandler(tornado.web.RequestHandler):
    @customized(default='index.html', template='user.index.html')
    def get(self):
        self.render(self.template)