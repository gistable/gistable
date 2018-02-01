# -*- coding: utf-8 -*-

__author__ = 'contee'

"""
asyncio producer-consumer
~~~~~~~~~~~~~~
"""

import asyncio, random

q = asyncio.Queue(maxsize=10)

@asyncio.coroutine
def produce():
    while True:
        i = random.randint(5,10)
        print(q.qsize())
        yield from q.put(i)
        yield from asyncio.sleep(2)

@asyncio.coroutine
def consume():
    while True:
        value = yield from q.get()
        yield from asyncio.sleep(value)
        print("Consumed", value)

loop = asyncio.get_event_loop()
asyncio.async(produce())
for x in range(3):
    asyncio.async(consume())
loop.run_forever()