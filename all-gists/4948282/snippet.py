from flask import request, Flask
from flask.ext import restful



class Api(restful.Api):
    def __init__(self, app, prefix='', default_mediatype='application/json',
            decorators=None):
        super(Api, self).__init__(app, prefix, default_mediatype, decorators)

        app.handle_exception = self.handle_exception
        app.handle_user_exception = self.handle_user_exception

        self.endpoints = {}

    def add_resource(self, resource, *urls, **kwargs):
        super(Api, self).add_resource(resource, *urls, **kwargs)

        endpoint = kwargs.get('endpoint', resource.__name__.lower())
        self.endpoints[endpoint] = list()
        for url in urls:
            self.endpoints[endpoint].append(self.prefix + url)

    def handle_exception(self, e):
        if(request.endpoint in self.endpoints.keys()):
            return super(Api, self).handle_error(e)
        else:
            return Flask.handle_exception(self.app, e)

    def handle_user_exception(self, e):
        if(request.endpoint in self.endpoints.keys()):
            return super(Api, self).handle_error(e)
        else:
            return Flask.handle_user_exception(self.app, e)
