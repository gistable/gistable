"""Script to download free O'Reilly ebooks."""
import asyncio
import os
import re
import sys
import aiohttp

filename_matcher = re.compile(r'http://www.oreilly.com/(.*)/free/(.*).csp')

session = None

async def main():
    global session
    session = aiohttp.ClientSession()
    tasks = []
    """Create directories and download ebooks."""
    if len(sys.argv) > 1:
        categories = sys.argv[1:]
    else:
        categories = ['business', 'data', 'design', 'iot', 'programming', 'security', 'web-platform', 'webops-perf']
    urls = ['http://www.oreilly.com/{}/free/'.format(x) for x in categories]
    fs = await asyncio.gather(*[retrieve_filenames(url) for url in urls])
    l = zip(list(zip(categories, urls)), fs)
    for (category, url), filenames in l:
        print(category)
        if not os.path.exists(category):
            os.makedirs(category)
        for title, (book_category, files) in filenames.items():
            path = os.path.join(category, title)
            if not os.path.exists(path):
                os.makedirs(path)
            print('\t{}'.format(title))
            for file in files:
                print('\t\t{}'.format(file))
                tasks.append(download_file(os.path.join(category, title, file),
                              'http://www.oreilly.com/{}/free/files/{}'.format(book_category, file)))

    await asyncio.wait(tasks)
    session.close()


async def download_file(path, url):
    """Download ebook files."""
    async with session.get(url) as r:
        with open(path, 'wb') as f:
            while True:
                chunk = await r.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)


async def retrieve_filenames(url):
    """Get ebook names."""
    async with session.get(url) as r:
        response = await r.text()
        matches = filename_matcher.findall(response)
        extensions = ['{}.pdf']  # options - '{}.pdf', '{}.mobi', '{}.epub'
        return {
            name: (category, [x.format(name) for x in extensions])
            for (category, name) in matches
            }


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
