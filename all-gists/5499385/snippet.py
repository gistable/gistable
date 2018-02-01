import tornado.web

class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
          # ...
          url(r"/static/(.*)", 
          tornado.web.StaticFileHandler if not options.debug else NoCacheStaticFileHandler, {
                "path": '/var/www/static' 
            }, name="static")