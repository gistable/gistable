import asyncio

@asyncio.coroutine
def waiting(r):
    print("hello from waiting -", r)
    yield from asyncio.sleep(2)
    print("bye from waiting -", r)
    return r


@asyncio.coroutine
def serial():
    a = yield from waiting(1)
    b = yield from waiting(2)
    c = yield from waiting(a + b)

    print(c)


@asyncio.coroutine
def parallel():
    a, b = yield from asyncio.gather(waiting(1), waiting(2))
    c = yield from waiting(a + b)

    print(c)


@asyncio.coroutine
def postponed():
    a = yield from waiting(1)
    b = yield from waiting(2)

    asyncio.Task(waiting('after'))
    return a + b


@asyncio.coroutine
def pp_caller():
    r = yield from postponed()
    print("got result from postponed -", r)
    yield from asyncio.sleep(3)
    loop.stop()


loop = asyncio.get_event_loop()

print("-- serial")
loop.run_until_complete(serial())

print("-- parallel")
loop.run_until_complete(parallel())

print("-- postponed")
asyncio.Task(pp_caller())
loop.run_forever()

loop.close()