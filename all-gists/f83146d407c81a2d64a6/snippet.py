import asyncio

@asyncio.coroutine
def open_file(name):
    print("opening {}".format(name))
    return open(name)

@asyncio.coroutine
def close_file(file):
    print("closing {}".format(file.name))
    file.close()

@asyncio.coroutine
def read_data(file):
    print("reading {}".format(file.name))
    return file.read()

@asyncio.coroutine
def process_data(filename):
    # I want the result from open_file(filename)
    # untill it's done don't bother calling me
    file = yield from asyncio.async(open_file(filename))
    print('opened {}'.format(filename))

    # I want the result from read_data(file)
    # untill it's done don't bother calling me
    data = yield from asyncio.async(read_data(file))

    print('read {}'.format(filename))

    yield from close_file(file)


@asyncio.coroutine
def main_coro(loop):
    # start our tasks asynchronously in futures
    tasks = [
        asyncio.async(process_data('/etc/passwd')),
        asyncio.async(process_data('/etc/group')),
        asyncio.async(process_data('/var/log/Xorg.0.log')),
    ]

    # untill all futures are done
    while not all(task.done() for task in tasks):
        # take a short nap
        yield from asyncio.sleep(0.01)

    # we're done, so stop the event loop
    loop.stop()


# get event loop
loop = asyncio.get_event_loop()

# schedule the main coroutine to start as soon as possible
loop.call_soon(asyncio.async, main_coro(loop))
# run untill explicitly stopped
loop.run_forever()

# instead of the above two lines we can also run
# loop.run_until_complete(main_coro()) and remove
# the loop parameter for main_coro and the call
# to loop.stop() at the end of it

loop.close()
