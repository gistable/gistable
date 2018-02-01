import re
import random
import base64
from scrapy import log

class RandomProxy(object):
    def __init__(self, settings):
        self.proxy_list = settings.get('PROXY_LIST')
        fin = open(self.proxy_list)

        self.proxies = {}
        for line in fin.readlines():
            parts = re.match('(\w+://)(\w+:\w+@)?(.+)', 'http://'+line)

            # Cut trailing @
            if parts.group(2):
                user_pass = parts.group(2)[:-1]
            else:
                user_pass = ''

            self.proxies[parts.group(1) + parts.group(3)] = user_pass

        fin.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if 'proxy' in request.meta:
            return

        proxy_address = random.choice(self.proxies.keys())
        proxy_user_pass = self.proxies[proxy_address]

        log.msg('Using proxy: {0}'.format(proxy_address))

        request.meta['proxy'] = proxy_address
        if proxy_user_pass:
            basic_auth = 'Basic ' + base64.encodestring(proxy_user_pass)
            request.headers['Proxy-Authorization'] = basic_auth

    def process_response(self, request, response, spider):
        if response.status in [403, 400] and 'proxy' in request.meta:
            log.msg('Response status: {0} using proxy {1} retrying request to {2}'.format(response.status, \
                request.meta['proxy'], request.url))
            proxy = request.meta['proxy']
            del request.meta['proxy']
            try:
                del self.proxies[proxy]
                log.msg('Removing banned proxy <%s>, %d proxies left' % (
                        proxy, len(self.proxies)))
            except KeyError:
                pass
            return request
        return response

    def process_exception(self, request, exception, spider):
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            del request.meta['proxy']
            try:
                del self.proxies[proxy]
                log.msg('Removing failed proxy <%s>, %d proxies left' % (
                        proxy, len(self.proxies)))
            except KeyError:
                pass

            return request
