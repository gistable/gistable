from functools import wraps
from types import FunctionType, GeneratorType
import logging
import time

def coroutine(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logging.debug('coroutine starting: {}'.format(f.__name__))
        return f(*args, **kwargs)
    return wrapper


class Future(object):

    def __init__(self):
        self._result = None
        self._done = False

    def set_result(self, result):
        self._result = result
        self._done = True

    @property
    def done(self):
        return bool(self._done)

    @property
    def result(self):
        return self._result

    def set_result(self, result):
        self._result = result
        self._done = True


class Task(Future):

    def __init__(self, generator):
        assert isinstance(generator, GeneratorType)
        Future.__init__(self)
        self._generator = generator
        self._yieldresult = None

    def step(self):
        try:
            if self._yieldresult is None:
                self._yieldresult = next(self._generator)
            else:
                self._yieldresult = self._generator.send(self._yieldresult)
            return self._yieldresult
        except StopIteration as stopiter:
            self.set_result(stopiter.value)
            return stopiter.value


class Loop(object):

    def __init__(self):
        self._queue = []

    def enqueue(self, task):
        assert isinstance(task, Task) or isinstance(task, GeneratorType)
        if not isinstance(task, Task):
            task = Task(task)
        self._queue.append(task)

    def run(self):
        while len(self._queue):
            task = self._queue.pop(0)
            result = task.step()
            logging.debug('step {}({}) = {}'.format(task.__class__.__name__,
                                                    id(task), result))
            if not task.done:
                self._queue.append(task)

#############################################################################

def do_work(n):
    for i in range(n):
        logging.debug('do_work: {}'.format(i))
        time.sleep(1)
        yield i
    return n

@coroutine
def demo(n):
    result = yield from do_work(n)
    logging.debug('result = {}'.format(result))
    return result

def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = Loop()
    loop.enqueue(demo(4))
    loop.enqueue(demo(1))
    loop.enqueue(demo(6))
    loop.run()

if __name__ == '__main__':
    main()