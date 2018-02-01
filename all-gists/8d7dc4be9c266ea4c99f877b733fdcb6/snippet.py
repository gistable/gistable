import asyncio
import aiohttp
import os
import random
import re
import sys
import traceback
from io import StringIO
from lxml.html import parse, make_links_absolute
from lxml.cssselect import CSSSelector
from lxml.html.clean import Cleaner
from urllib.parse import urlparse
from urllib.request import url2pathname


class Spider:
    def __init__(self, main, urlfilter, selector, limit=100000, tasks=1):
        self._limit = limit
        self._main = main
        self._filter = urlfilter
        self._selector = selector
        loop = asyncio.get_event_loop()
        self._q = asyncio.Queue(loop=loop)
        self._session = aiohttp.ClientSession(loop=loop)
        self._workers = [asyncio.Task(self._work()) for i in range(tasks)]
        self._seen = set()
        self._done = 0
        directory = os.path.dirname(os.path.realpath(__file__))
        self._data_directory = os.path.join(directory, '..', 'data', main)
        self._ensure_directory(self._data_directory)

    def __del__(self):
        self._session.close()

    def _save(self, html, url):
        print(url)
        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.style = True
        h = self._selector(cleaner.clean_html(html))
        text = "\n".join([p.text_content() for p in h if
                          p.text_content() is not None])
        path = url2pathname(urlparse(url).path)[:-1]
        path = os.path.join(self._data_directory, path[1:])

        if text:
            self._ensure_directory(os.path.dirname(path))
            with open(path, 'w') as f:
                f.write(text)

    def _ensure_directory(self, directory):
        os.makedirs(directory, exist_ok=True)

    async def _parse(self, text, url):
        content = await text
        sel = CSSSelector('a')
        try:
            html = parse(StringIO(make_links_absolute(content, self._main)))
        except:
            return

        for el in sel(html):
            href = el.get('href')
            if (href is not None and
                href not in self._seen and
                ('http://' + self._main in href or
                 'https://' + self._main in href)):
                self._q.put_nowait(href)
            self._seen.add(href)

        if re.match(self._filter, url):
            self._save(html, url)

        self._done += 1
        sys.stdout.write("Scraped %i pages, last %s                          \r" % (self._done, url))

    async def _work(self):
        while True:
            page = await self._q.get()
            try:
                if self._done < self._limit:
                    with aiohttp.Timeout(10):
                        async with self._session.get(page) as resp:
                            if resp.status == 200:
                                await self._parse(resp.text(), page)
                                await asyncio.sleep(1.0 * random.random())
                            elif resp.status == 503:
                                await asyncio.sleep(5)
                            else:
                                print("REDIRECT! %s" % page)
            except Exception as err:
                traceback.print_exc()
                print("%s" % err)
            self._q.task_done()

    async def run(self):
        await self._q.put('http://' + self._main)
        await self._q.join()
        for w in self._workers:
            w.cancel()


def err(loop, context):
    print("error in loop: %s context: %s" % (loop, context))


a = [
    Spider('www.nytimes.com', r"https?://www\.nytimes\.com/\d{4}.*",
           CSSSelector('.story-body-text')),
    Spider('www.thenation.com', r"https?://www\.thenation\.com/article.*",
           CSSSelector('.article-body p')),
    Spider('www.washingtonpost.com',
           r"https?://www\.washingtonpost\.com/.*/\d{4}/\d{2}.*",
           CSSSelector('#article-body article')),
    Spider('dailycaller.com',
           r"https?://dailycaller\.com/\d{4}.*",
           CSSSelector('#dc-word-up')),
    Spider('www.buzzfeed.com',
           r"https?://www\.buzzfeed\.com/.*",
           CSSSelector('.c p')),
    Spider('www.thedailybeast.com',
           r"https?://www\.thedailybeast\.com/articles/.*",
           CSSSelector('.BodyNodes .Text')),
    Spider('www.huffingtonpost.com',
           r"https?://www\.huffingtonpost\.com/.*",
           CSSSelector('.text p')),
    Spider('www.vox.com',
           r"https?://www\.vox\.com/\d{4}/.*",
           CSSSelector('.c-entry-content p')),
    Spider('www.breitbart.com',
           r"https?://www\.breitbart\.com/.*",
           CSSSelector('.the-article p, h2')),
    Spider('nypost.com',
           r"https?://nypost\.com/\d{4}.*",
           CSSSelector('.entry-content p')),
    Spider('www.nydailynews.com',
           r"https?://www\.nydailynews\.com/.*",
           CSSSelector('article p'))
]


loop = asyncio.get_event_loop()
loop.set_exception_handler(err)
loop.run_until_complete(asyncio.gather(*[asyncio.ensure_future(i.run()) for i in a]))
