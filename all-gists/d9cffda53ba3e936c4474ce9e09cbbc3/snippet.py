import asyncio
import functools
import time
import urllib.parse

import aiohttp


def throttling(sleep):
    def decorator(func):
        last_called = None
        lock = asyncio.Lock()

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_called

            async with lock:
                now = time.monotonic()

                if last_called is not None:
                    delta = now - last_called

                    if delta < sleep:
                        await asyncio.sleep(sleep - delta)

                try:
                    return await func(*args, **kwargs)
                finally:
                    last_called = time.monotonic()

        return wrapper

    return decorator


_domain_funcq_map = {}
DOMAIN_CONCURRENCY = 2


async def get_page(url):
    domain = urllib.parse.urlparse(url).hostname

    if domain not in _domain_funcq_map:
        q = _domain_funcq_map[domain] = asyncio.Queue()
        for _ in range(DOMAIN_CONCURRENCY):
            q.put_nowait(throttling(1)(_get_page))

    func = await _domain_funcq_map[domain].get()

    try:
        return await func(url)
    finally:
        _domain_funcq_map[domain].put_nowait(func)


async def _get_page(url):
    async with await aiohttp.get(url) as resp:
        body = await resp.read()

    return body


if __name__ == '__main__':
    urls = [
        'http://localhost/1',
        'http://localhost/2',
        'http://localhost/3',
        'http://localhost/4',
        'http://localhost/5',
        'http://localhost.localdomain/6',
    ]

    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(asyncio.wait([get_page(u) for u in urls])))
