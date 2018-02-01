import asyncio
import functools
from collections import OrderedDict


def async_lru(size=100):
    cache = OrderedDict()

    def decorator(fn):
        @functools.wraps(fn)
        async def memoizer(*args, **kwargs):
            key = str((args, kwargs))
            try:
                cache[key] = cache.pop(key)
            except KeyError:
                if len(cache) >= size:
                    cache.popitem(last=False)
                cache[key] = await fn(*args, **kwargs)
            return cache[key]
        return memoizer
    return decorator