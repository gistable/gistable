from django.core.conf import settings

class DbgResponse(object):
    def process_response(self, request, response):
        """Add html, head, and body tags so debug toolbar will activate."""
        if request.GET.get('dbg') and settings.DEBUG:
            cnt = response.content
            if '<body>' not in cnt:
                response.content = '<html><head></head><body>%s</body></html>' % cnt
                if 'content_type' in response._headers:
                    hdr = response._headers['content_type']
                    response._headers['content_type'] = (hdr[0], 'text/html')
        return response