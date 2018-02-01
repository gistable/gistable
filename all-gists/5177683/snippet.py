from django.http import HttpResponse
from django.conf import settings

CORS_ALLOW_ORIGIN = getattr(settings, 'CORS_ALLOW_ORIGIN', '*')
CORS_ALLOW_METHODS = getattr(settings, 'CORS_ALLOW_METHODS', ['POST', 'GET', 'PUT', 'DELETE', 'OPTIONS'])
CORS_ALLOW_HEADERS = getattr(settings, 'CORS_ALLOW_HEADERS', ['content-type', 'authorization'])
CORS_ALLOW_CREDENTIALS = getattr(settings, 'CORS_ALLOW_CREDENTIALS', True)

class CorsMiddleware(object):
    def _set_headers(self, response):
        response['Access-Control-Allow-Origin'] = CORS_ALLOW_ORIGIN
        response['Access-Control-Allow-Methods'] = ','.join(CORS_ALLOW_METHODS)
        response['Access-Control-Allow-Headers'] = ','.join(CORS_ALLOW_HEADERS)
        response['Access-Control-Allow-Credentials'] = 'true' if CORS_ALLOW_CREDENTIALS else 'false'

        return response

    def process_request(self, request):
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            return self._set_headers(HttpResponse())

    def process_response(self, request, response):
        return self._set_headers(response)