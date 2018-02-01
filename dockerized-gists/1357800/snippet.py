from functools import wraps


def memoise(wrapped):
    cache = {}

    @wraps(wrapped)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = wrapped(*args, **kwargs)
        return cache[key]

    return wrapper

"""
@memoise
def test(*args, **kargs):
    return 'fubar'
"""
