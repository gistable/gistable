from tornado.ioloop import IOLoop

def debounce(seconds):
    """Decorator that will postpone calling a function until after seconds
    have elapsed since the last time it was invoked. Not to be confused
    with a throttle."""

    def decorator(fn):

        def wrapper(*args, **kwargs):
            io_loop = IOLoop.current()
            if hasattr(wrapper, 'delayed_call'):
                io_loop.remove_timeout(wrapper.delayed_call)
            wrapper.delayed_call = io_loop.call_later(
                seconds, fn, *args, **kwargs)

        return wrapper

    return decorator