# coding: utf-8
import time
from collections import OrderedDict


class Cache():
    """
    In process memory cache. Not thread safe.
    Usage:
    
    cache = Cache(max_size=5)
    cache.set("python", "perfect", timeout=10)
    cache.get("python")
    >>> perfect
    time.sleep(11)
    cache.get("python")
    >>> None
    cache.get("python", "perfect anyway")
    >>> perfect anyway
    cache.clear()
    """
    def __init__(self, max_size=1000, timeout=None):
        self._store = OrderedDict()
        self._max_size = max_size
        self._timeout = timeout

    def set(self, key, value, timeout=None):
        self._check_limit()
        if not timeout:
            timeout = self._timeout
        if timeout:
            timeout = time.time() + timeout
        self._store[key] = (value, timeout)

    def get(self, key, default=None):
        data = self._store.get(key)
        if not data:
            return default
        value, expire = data
        if expire and time.time() > expire:
            del self._store[key]
            return default
        return value

    def _check_limit(self):
        """
        check if current cache size exceeds maximum cache
        size and pop the oldest item in this case
        """
        if len(self._store) >= self._max_size:
            self._store.popitem(last=False)

    def clear(self):
        """
        clear all cache
        """
        self._store = OrderedDict()