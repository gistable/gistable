import threading
import functools
import logging

def timeout(duration, default=None):
    def decorator(func):
        class InterruptableThread(threading.Thread):
            def __init__(self, args, kwargs):
                threading.Thread.__init__(self)
                self.args = args
                self.kwargs = kwargs
                self.result = default
                self.daemon = True

            def run(self):
                try:
                    self.result = func(*self.args, **self.kwargs)
                except Exception:
                    pass

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            it = InterruptableThread(args, kwargs)
            it.start()
            it.join(duration)
            if it.isAlive():
                logging.warning('timeout in function {0}: args: {1}, kwargs: {2}'.format(func, args, kwargs))
            return it.result
        return wrap
    return decorator