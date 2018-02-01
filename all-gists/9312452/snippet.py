import asyncio
import aiohttp
import bs4
import tqdm


@asyncio.coroutine
def get(*args, **kwargs):
    response = yield from aiohttp.request('GET', *args, **kwargs)
    return (yield from response.read_and_close(decode=True))


@asyncio.coroutine
def wait_with_progress(coros):
    for f in tqdm.tqdm(asyncio.as_completed(coros), total=len(coros)):
        yield from f


def first_magnet(page):
    soup = bs4.BeautifulSoup(page)
    a = soup.find('a', title='Download this torrent using magnet')
    return a['href']


@asyncio.coroutine
def print_magnet(query):
    url = 'http://thepiratebay.se/search/{}/0/7/0'.format(query)
    with (yield from sem):
        page = yield from get(url, compress=True)
    magnet = first_magnet(page)
    print('{}: {}'.format(query, magnet))


distros = ['archlinux', 'ubuntu', 'debian']
sem = asyncio.Semaphore(5)
loop = asyncio.get_event_loop()
f = asyncio.wait([print_magnet(d) for d in distros])
loop.run_until_complete(f)
