"Memcached cache backend"

from django.core.cache.backends import memcached
from django.utils.encoding import smart_unicode, smart_str

MIN_COMPRESS_LEN = 150000

class CacheClass(memcached.CacheClass):
    def add(self, key, value, timeout=None, min_compress_len=MIN_COMPRESS_LEN):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if timeout is None:
            timeout = self.default_timeout
        return self._cache.add(smart_str(key), value, timeout, min_compress_len)

    def set(self, key, value, timeout=None, min_compress_len=MIN_COMPRESS_LEN):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if timeout is None:
            timeout = self.default_timeout
        self._cache.set(smart_str(key), value, timeout)

    def set_many(self, data, timeout=None, min_compress_len=MIN_COMPRESS_LEN):
        safe_data = {}
        for key, value in data.items():
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            safe_data[smart_str(key)] = value
        if timeout is None:
            timeout = self.default_timeout
        self._cache.set_multi(safe_data, timeout, min_compress_len=min_compress_len)
