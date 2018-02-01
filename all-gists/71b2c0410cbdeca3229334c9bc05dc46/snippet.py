import asyncio
import functools
import json
import secrets

import aiohttp

from concurrent.futures import ALL_COMPLETED


class FeedUpdater:
    def __init__(self, feeds, loop):
        self.feeds = feeds
        self.loop = loop
        self.session = aiohttp.ClientSession(loop=loop)

    async def _fetch(self, url):
        async with self.session.get(url) as response:
            status = response.status
            assert status == 200
            data = await response.text()
            return url, data

    async def __call__(self):
        tasks = [self._fetch(url) for url in self.feeds.keys()]
        done, pending = await asyncio.wait(
            tasks,
            loop=self.loop,
            return_when=ALL_COMPLETED
        )
        for task in done:
            url, data = task.result()
            self.feeds[url] = f"{len(data)}.{secrets.token_hex(4)}"

        # TODO placeholder
        print(json.dumps(self.feeds, sort_keys=True, indent=4))

    def __del__(self):
        self.session.close()

def schedule(func, args=None, kwargs=None, interval=60, *, loop):
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    async def periodic_func():
        while True:
            await func(*args, **kwargs)
            await asyncio.sleep(interval, loop=loop)

    return loop.create_task(periodic_func())
create_scheduler = lambda loop: functools.partial(loop=loop)

# USAGE =====================================================

loop = asyncio.new_event_loop()
schedule = create_scheduler(loop=loop)

feeds = {
    "http://feeds.abcnews.com/abcnews/topstories": None,
    "http://www.feedforall.com/sample.xml": None
}
update = FeedUpdater(feeds=feeds, loop=loop)

refresh_task = schedule(update, interval=3)
loop.run_forever()