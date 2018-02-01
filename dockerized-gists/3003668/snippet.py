class CORSMiddleware(object):
    """Enable serving of CORS requests (http://en.wikipedia.org/wiki/Cross-origin_resource_sharing)"""

    ALLOW_ORIGIN = "*"
    ALLOW_HEADERS = "Origin, X-Requested-With, Content-Type"

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            start_response('200 OK', [
                ('Access-Control-Allow-Origin', self.ALLOW_ORIGIN),
                ('Access-Control-Allow-Headers', self.ALLOW_HEADERS),
            ])
            return ['POST']
        else:
            def cors_start_response(status, headers, exc_info=None):
                headers.append(('Access-Control-Allow-Origin', self.ALLOW_ORIGIN))
                headers.append(('Access-Control-Allow-Headers', self.ALLOW_HEADERS))
                return start_response(status, headers, exc_info)

            return self.app(environ, cors_start_response)