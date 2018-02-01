import sys
import cProfile
import pstats

from functools import wraps
from contextlib import contextmanager


@contextmanager
def profile():
    pr = cProfile.Profile()
    pr.enable()

    yield

    pr.disable()
    ps = pstats.Stats(pr, stream=sys.stdout).sort_stats('cumulative')
    ps.print_stats(20)


def with_profiling(fn):
    """
    Use as a decorator to add profiling to a function.

    """
    @wraps(fn)
    def profiled_function(*args, **kwargs):
        print('Profiling %s in %s' % (fn.__name__, fn.__module__, ))
        with profile():
            return fn(*args, **kwargs)
    return profiled_function
