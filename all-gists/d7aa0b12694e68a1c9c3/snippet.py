import asyncio
import concurrent.futures
import requests


Seconds = [
    ("first", 5),
    ("second", 0),
    ("third", 3)
]


async def sleeping(order, seconds, hook=None):
    await asyncio.sleep(seconds)
    if hook:
        hook(order)
    return order


async def basic_async():
    # the order of result is nonsequential (not depends on order, even sleeping time)
    for s in Seconds:
        r = await sleeping(*s)
        print("{0} is finished.".format(r))
    return True


async def parallel_by_gather():
    # execute by parallel
    def notify(order):
        print(order + " has just finished.")

    cors = [sleeping(s[0], s[1], hook=notify) for s in Seconds]
    results = await asyncio.gather(*cors)
    return results


async def parallel_by_wait():
    # execute by parallel
    def notify(order):
        print(order + " has just finished.")

    cors = [sleeping(s[0], s[1], hook=notify) for s in Seconds]
    done, pending = await asyncio.wait(cors)
    return done, pending


async def queue_execution(arg_urls, callback, parallel=2):
    # see refs
    # http://stackoverflow.com/questions/22190403/how-could-i-use-requests-in-asyncio

    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    for u in arg_urls:
        queue.put_nowait(u)

    async def fetch(q):
        while not q.empty():
            u = await q.get()
            future = loop.run_in_executor(None, requests.get, u)
            future.add_done_callback(callback)
            await future

    tasks = [fetch(queue) for i in range(parallel)]
    return await asyncio.wait(tasks)


async def limited_parallel(limit=3):
    sem = asyncio.Semaphore(limit)

    # function want to limit the number of parallel
    async def limited_sleep(num):
        with await sem:
            return await sleeping(str(num), num)

    import random
    tasks = [limited_sleep(random.randint(0, 3)) for i in range(9)]
    return await asyncio.wait(tasks)


async def future_callback(callback):
    futures = []

    for s in Seconds:
        cor = sleeping(*s)
        f = asyncio.ensure_future(cor)
        f.add_done_callback(callback)
        futures.append(f)

    await asyncio.wait(futures)


def get_async_iterator(arg_urls):

    class AsyncIterator():

        def __init__(self, urls):
            self.urls = iter(urls)
            self.__loop = None

        async def __aiter__(self):
            self.__loop = asyncio.get_event_loop()
            return self

        async def __anext__(self):
            try:
                u = next(self.urls)
                future = self.__loop.run_in_executor(None, requests.get, u)
                resp = await future
            except StopIteration:
                raise StopAsyncIteration
            return resp


    return AsyncIterator(arg_urls)


def print_num(num):
    print(num)

async def async_by_process():
    executor = concurrent.futures.ProcessPoolExecutor()
    queue = asyncio.Queue()

    for i in range(10):
        queue.put_nowait(i)

    async def proc(q):
        while not q.empty():
            i = await q.get()
            future = loop.run_in_executor(executor, print_num, i)
            await future

    tasks = [proc(queue) for i in range(4)]  #cpu core
    return await asyncio.wait(tasks)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    print("@basic async ******************************************")
    loop.run_until_complete(basic_async())

    print("@parallel by gather ***********************************")
    # the result of asyncio.gather is mysterious!
    results = loop.run_until_complete(parallel_by_gather())
    for r in results:
        print("asyncio.gather result: {0}".format(r))

    print("@parallel by wait *************************************")
    done, pending = loop.run_until_complete(parallel_by_wait())
    for d in done:
        dr = d.result()
        print("asyncio.wait result: {0}".format(dr))

    print("@queue execution **************************************")
    results = []
    def store_result(f):
        results.append(f.result())
    results.clear()
    loop.run_until_complete(queue_execution([
        "http://www.google.com",
        "http://www.yahoo.com",
        "https://github.com/"
    ], store_result))
    for r in results:
        print("queue execution: {0}".format(r.url))

    print("@limited parallel **************************************")
    done, pending = loop.run_until_complete(limited_parallel())
    for d in done:
        print("limited parallel: {0}".format(d.result()))

    print("@future callback **************************************")
    results.clear()
    loop.run_until_complete(future_callback(store_result))
    for r in results:
        print("future callback: {0}".format(r))

    print("@async iterator ***************************************")
    async def async_fetch(urls):
        ai = get_async_iterator(urls)
        async for resp in ai:
            print(resp.url)

    loop.run_until_complete(async_fetch([
        "http://www.google.com",
        "http://www.yahoo.com",
        "https://github.com/"
    ]))

    print("@async by process *************************************")
    loop.run_until_complete(async_by_process())
