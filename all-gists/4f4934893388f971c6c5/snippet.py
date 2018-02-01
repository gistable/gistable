"""
Simple example of building your own context manager.

Resources:

- http://preshing.com/20110920/the-python-with-statement-by-example/
- https://docs.python.org/3/library/contextlib.html
- PEP 343 -- the "with" statement: https://www.python.org/dev/peps/pep-0343/

"""

from contextlib import ContextDecorator
from contextlib import contextmanager
from time import sleep, time


class Timed():
    """A simple "timer" context manager. It prints execution time."""

    def __enter__(self):
        self.start = time()
        print("Starting at {}".format(self.start))
        return self

    def __exit__(self, type, value, traceback):
        # This code is guaranteed to run
        if traceback:
            print("type: {}".format(type))
            print("value: {}".format(value))
            print("traceback: {}".format(traceback))

        self.end = time()
        total = self.end - self.start
        print("Ending at {} (total: {})".format(self.end, total))


@contextmanager
def timed():
    """A simple timer context manager, implemented using a generator function"""
    start = time()
    print("Staring at {}".format(start))

    yield

    end = time()
    print("Ending at {} (total: {})".format(end, end - start))


@contextmanager
def robust_timed():
    """A slighly more robust timer context manager, implemented using a
    generator function. This one will report time even if an exception occurs"""
    start = time()
    print("Staring at {}".format(start))
    try:
        yield
    finally:
        end = time()
        print("Ending at {} (total: {})".format(end, end - start))


class bettertimed(ContextDecorator):
    """A better timed class. This uses the ContextDecorator, which allows us
    to use this as a decorator, too!
    """

    def __enter__(self):
        self.start = time()
        print("Starting at {}".format(self.start))
        return self

    def __exit__(self, type, value, traceback):
        self.end = time()
        total = self.end - self.start
        print("Ending at {} (total: {})".format(self.end, total))



def go():
    # Using the Class...
    with Timed():
        print("sleeping for 2...")
        sleep(2)

#    # When there's an exception
#    with Timed():
#        print("sleeping for 2...")
#        sleep(2)
#        assert(False)  # Timed will still finish & give you the end/total
#
#    # Support for the 'as' keyword.
#    with Timed() as timer:
#        print("sleeping for 2...")
#        sleep(2)
#        print("ok, we started {}s ago".format(time() - timer.start))
#        sleep(2)
#
#    # As a function
#    with timed():
#        print("sleeping for 2...")
#        sleep(2)
#
#    # When there's an exception
#    with timed():
#        print("sleeping for 2...")
#        sleep(2)
#        assert(False)  # fails... we dont' get the ending time.
#
#
#    # Unless we use the robust version
#    with robust_timed():
#        print("sleeping for 2...")
#        sleep(2)
#        assert(False)  # We should still get the ending time.
#
#    # Using the ContextDecorator subclass as a context manager...
#    with bettertimed():
#        sleep(1)
#        print("ok... ")
#        sleep(1)
#
#    # And as a decorator for a function.
#    @bettertimed()
#    def slow_print(text):
#        sleep(1)
#        print(text)
#        sleep(1)
#
#    # Calling that function to test it out.
#    slow_print('oh bother')
