from threading import Event

class TimeoutError(Exception):
    pass

def asynctest(timeout=None):
    def decorator(func):
        def wrapper(self):
            func(self)
            self.async_wait(timeout)

            if not self.async_done():
                raise TimeoutError

            self.async_release()
        return wrapper

    return decorator


class AsyncTestCase(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super(AsyncTestCase, self).__init__(methodName)
        self.async = threading.Event()

    def async_wait(self, timeout=None):
        return self.async.wait(timeout)

    def async_release(self):
        return self.async.set()

    def async_done(self):
        return self.async.is_set()