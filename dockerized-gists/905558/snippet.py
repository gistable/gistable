class HTTPSMixin(object):

    def is_secure(self):
        return self.request.headers.get('X-Scheme') == 'https'

    def httpify_url(self, url=None):
        url = url if url else self.request.full_url()
        if url.startswith('/'):
            parsed = urlparse(self.request.full_url())
            return 'http://%s%s' % (parsed.netloc, url)
        else:
            return url.replace('https://', 'http://')

    def httpsify_url(self, url=None):
        url = url if url else self.request.full_url()
        if url.startswith('/'):
            parsed = urlparse(self.request.full_url())
            return 'https://%s%s' % (parsed.netloc, url)
        else:
            return url.replace('http://', 'https://')
