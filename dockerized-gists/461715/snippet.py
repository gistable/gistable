import time

from contextlib import contextmanager

@contextmanager
def easyprofile(msg):
    before = time.time()
    yield
    print '%s took %0.2fsec' % (msg, time.time() - before)

if __name__ == '__main__':
    with easyprofile('Executing an expensive query'):
        results = get_expensive_data()
    # Do something with the results