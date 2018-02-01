import cProfile
import functools

def do_cprofile(*dec_args):
    """
    Decorator for profiling functions.

    If a file name is passed to the decorator as an argument, profiling data
    will be written to that file; otherwise, it will be displayed on the screen.
    """

    def wrap_save(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            profile = cProfile.Profile()
            try:
                profile.enable()
                result = f(*args, **kwargs)
                profile.disable()
                return result
            finally:
                profile.dump_stats(dec_args[0])
        return wrapper

    def wrap_print(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            profile = cProfile.Profile()
            try:
                profile.enable()
                result = f(*args, **kwargs)
                profile.disable()
                return result
            finally:
                profile.print_stats()
        return wrapper

    if len(dec_args) == 1 and callable(dec_args[0]):
        return wrap_print(dec_args[0])
    elif len(dec_args) == 0:
        return wrap_print
    else:
        return wrap_save

if __name__ == '__main__':
    import numpy as np
    import numpy.linalg

    @do_cprofile('out')
    def foo(x):
        """
        My function.
        """
        return np.linalg.pinv(x)

    foo(np.random.rand(10, 10))
