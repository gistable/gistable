"""Provide an executor to run asyncio coroutines in a shadow thread."""

import asyncio
from threading import Thread
from concurrent.futures import Executor


class AsyncioExecutor(Executor):

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._target)
        self._thread.start()

    def _target(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, fn, *args, **kwargs):
        coro = fn(*args, **kwargs)
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def shutdown(self, wait=True):
        self._loop.call_soon_threadsafe(self._loop.stop)
        if wait:
            self._thread.join()


def test():
    print('Starting asyncio executor...')
    with AsyncioExecutor() as executor:
        future1 = executor.submit(asyncio.sleep, 1, result=1)
        future2 = executor.submit(asyncio.sleep, 2, result=2)
        future3 = executor.submit(asyncio.sleep, 3, result=3)
        print('Result of asyncio.sleep(1, result=1):', future1.result())
        print('Result of asyncio.sleep(2, result=2):', future2.result())
        print('Result of asyncio.sleep(3, result=3):', future3.result())


def countdown(n):
    count = range(n+1)
    results = count[::-1]
    print('Counting down...')
    with AsyncioExecutor() as executor:
        for result in executor.map(asyncio.sleep, count, results):
            print(result)


if __name__ == '__main__':
    test()
    print()
    countdown(10)
