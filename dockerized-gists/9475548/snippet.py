import contextlib
from datetime import datetime


class Timer(object):

    def start(self):
        self.start = datetime.now()

    def stop(self):
        self.stop = datetime.now()

    def elapsed(self):
        return self.stop - self.start

    def assertHasDate(self, date):
        assert self.start <= date <= self.stop, \
               "%s was not during the timer" % date

    def assertNotHasDate(self, date):
        assert not (self.start <= date <= self.stop), \
               "%s was during the timer" % date


@contextlib.contextmanager
def timekeeper():
    t = Timer()
    t.start()
    try:
        yield t
    finally:
        t.stop()

if __name__ == "__main__":
    t1 = Timer()

    t1.start()
    for i in range(100000):
        pass
    t1.stop()
    print "elapsed", t1.elapsed()

    with timekeeper() as t2:
        d = datetime.now()
    t2.assertHasDate(d)