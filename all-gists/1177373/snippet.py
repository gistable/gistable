import redis

from scrapy.dupefilter import BaseDupeFilter
from scrapy.utils.request import request_fingerprint


class RedisDupeFilter(BaseDupeFilter):

    def __init__(self, host, port):
        self.redis = redis.Redis(host, port)

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        return cls(host, port)

    def request_seen(self, request):
        fp = request_fingerprint(request)
        added = self.redis.sadd('fingerprints', fp)
        return not added
