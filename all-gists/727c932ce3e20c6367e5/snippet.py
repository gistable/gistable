import asyncio
import random

@asyncio.coroutine
def print_whenever(identifier):
    """a little function that prints at random intervals"""
    while True:
        yield from asyncio.sleep(random.choice([0.5, 1, 1.3]))
        print('hi from', identifier)


@asyncio.coroutine
def start_things():
    """start several little printey functions at the same time"""
    for i in range(5):
        # this works - it kicks off our printer "in the background"
        asyncio.get_event_loop().create_task(
          print_whenever(i)
        )

        # this doesn't -- it never gets past the first item
        # yield from print_whenever(i)

# tell asyncio to start running start_things
loop = asyncio.get_event_loop()
loop.create_task(start_things())
loop.run_forever()
