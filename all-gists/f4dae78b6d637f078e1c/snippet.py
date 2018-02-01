import asyncio
import logging
import time

import psutil


logger = logging.getLogger(__name__)


@asyncio.coroutine
def pace_maker(tasks):
    for task in tasks:
        task()

    o = time.time()
    logger.debug("Called at", o)
    yield from asyncio.sleep(1-(o-int(o)))
    yield from pace_maker(tasks)


def cpu_percent():
    p =  psutil.cpu_percent()
    print("CPU usage", p, "%:", '*'*int(p // 10))


def main():
    asyncio.Task(pace_maker([cpu_percent]))
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    main()

