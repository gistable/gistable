import itertools
from operator import itemgetter

def iunzip(iterable):
    """Iunzip is the same as zip(*iter) but returns iterators, instead of 
    expand the iterator. Mostly used for large sequence"""

    _tmp, iterable = itertools.tee(iterable, 2)
    iters = itertools.tee(iterable, len(_tmp.next()))
    return (itertools.imap(itemgetter(i), it) for i, it in enumerate(iters))
