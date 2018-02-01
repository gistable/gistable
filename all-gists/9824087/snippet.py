from threading import Thread, Semaphore


class FirstToReturn:
    def __init__(self):
        self._tasks = []
        self._results = []
        self._signal = Semaphore()

    def run(self, fn, *args, **kwargs):
        thread = Thread(target=self._perform, args=[fn, args, kwargs])
        thread.daemon = True
        self._tasks.append(thread)
        thread.start()

    def get_result(self):
        while not self._done():
            self._signal.acquire()
        return max(self._results)

    def _perform(self, fn, args, kwargs):
        self._results.append(fn(*args, **kwargs))
        self._signal.release()

    def _done(self):
        return any(self._results) or len(self._results) == len(self._tasks)


# Test code ...
###############

from time import sleep


def do_something(wait, result=None):
    sleep(wait)
    return result

w = FirstToReturn()
w.run(do_something, 1)
w.run(do_something, 2)
w.run(do_something, 3)
w.run(do_something, 2, 'first')
w.run(do_something, 10)
w.run(do_something, 10, 'second')

print w.get_result()  # should take ~2s and print 'first'
