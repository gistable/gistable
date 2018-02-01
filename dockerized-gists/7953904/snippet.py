# -*- coding: utf-8 -*-
from functools import wraps, partial
from redis import Redis

redis_client = Redis()


class redis_memoize(object):
    """cache the return value of a method into redis

    This class is meant to be used as a decorator of methods. The return value
    from a given method invocation will be cached in the redis with
    customisable key.
    All arguments passed to a method decorated with memoize must be hashable.

    class Obj(object):
        @memoize(cache_key="foobar:{0}-{2}")
        def get_15(self, foo, bar, baz):
            return 16

    So after the call of Obj().get_15("a", "b", "c")
    result of method call will be saved to redis with key
    foobar:a-c
    """

    def __init__(self, cache_key=None):
        self.cache_key = cache_key

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)

    def __call__(self, *args, **kw):
        obj = args[0]

        if not hasattr(self, "func"):
            self.func = obj
            return self

        if self.cache_key:
            key = self.cache_key.format(*args[1:], **kw)
        else:
            prefix = "%s.%s.%s" % (obj.__class__.__name__,
                                   obj.__module__,
                                   self.func.__name__)
            key = (prefix, args[1:], tuple(frozenset(kw.items())))

        if redis_client.exists(key):
            res = redis_client.get(key)
        else:
            res = self.func(*args, **kw)
            redis_client.set(key, res)

        return res