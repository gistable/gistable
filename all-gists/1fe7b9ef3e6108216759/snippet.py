saved = {}

def web_lookup(url):
    if url in saved:
        return saverd[url]
    page = urrlib.urlopen(url).read()
    saved[url] = page
    return page

# NEEDS TO BE A PURE FUNCTION, NO SIDE EFFECTS LIKE PRINT

# PYTHON 3
from functools import lru_cache
@lru_cache(maxsize=None)
def web_lookup(url):
    return urrlib.urlopen(url).read()


# PYTHON 2
@cache
def web_lookup(url):
    return urrlib.urlopen(url).read()

from functools import wraps

def cache(func):
    saved = {}
    @wraps(func)
    def newfunc(*args):
        if args in saved:
            return saved[args]
        result = func(*args)
        saved[args] = result
        return result
    return newfunc