import os
import inspect
from functools import wraps


_file_cache = {}


def cache_file(path):
    def cache_is_fresh(name):
        return _file_cache[name]['MTIME'] == os.path.getmtime(path)

    def func_has_args(func):
        args, varargs, keywords, defaults = inspect.getargspec(func)
        count = len(list(set(args) - set(['self'])))  # Substract 'self' from
                                                      # args and count args
        if varargs:
            count += 1
        if keywords:
            count += 1
        return count > 0

    def decorator(f):
        if func_has_args(f):
            raise SyntaxWarning('cache_file doesn\'t support arguments')

        name = f.__name__

        @wraps(f)
        def return_cache(*args, **kwargs):
            if name in _file_cache.keys() and cache_is_fresh(name):
                return _file_cache[name]['CONTENTS']

            else:
                # Store to cache
                _file_cache[name] = {
                    'MTIME': os.path.getmtime(path),
                    'CONTENTS': f(*args, **kwargs)
                }
                return _file_cache[name]['CONTENTS']
        return return_cache

    return decorator


# Example:
counter = 0

@cache_file('/tmp/cached-file')
def my_func():
    global counter
    counter += 1
    return counter