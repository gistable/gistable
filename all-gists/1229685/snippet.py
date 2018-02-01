from django.conf import settings
from django.db import connection

class SqldumpMiddleware(object):
    def process_response(self, request, response):
        if settings.DEBUG and 'sqldump' in request.GET:
            response.content = str(connection.queries)
            response['Content-Type'] = 'text/plain'
        return response
