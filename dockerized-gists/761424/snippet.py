import functools
import thread

def nonblocking(func):
    """
    Decorator that runs the given func in a separate thread 
    when called, eg::

        @nonblocking
        def some_blocking_func():
            # Some long running code.
            return

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        thread.start_new_thread(func, args, kwargs)
    return wrapper