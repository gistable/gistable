#!/usr/bin/env python3
from threading import Thread
from urllib.parse import unquote
from pathlib import Path
from queue import Queue
import requests
import os.path
import sys
import re


INDEX_PAGE = 'http://rule34.paheal.net/post/list/%s/%d'
RE_IMG_URL = r'href=\"(.*)\"\>Image Only'
RE_TOTAL_PAGES = r'\/(\d+)\"\>Last\<\/a\>'
RE_BAD_FILENAME = r'[^\w\s\-\.\~\!\@\#\$\%\^\(\)\+\=\']'

DOWNLOAD_THREAD = 10

def fetch_total_pages(kw):
    resp = requests.get(INDEX_PAGE % (kw, 1))
    match = re.search(RE_TOTAL_PAGES, resp.text)
    if match is None:
        # No <a>Last</a> tag if only 1 page.
        return 1
    return int(match.group(1))


def fetch_urls(kw, page_from, page_to):
    for i in range(page_from, page_to + 1):
        resp = requests.get(INDEX_PAGE % (kw, i))
        urls = re.findall(RE_IMG_URL, resp.text)
        print('%s images are found in page %s.' % (len(urls), i))
        for url in urls:
            yield url


def download(queue, path, tid):
    while True:
        url = queue.get()
        if url is None:
            break
        fname = unquote(url).split('/')[-1]
        fname = re.sub(RE_BAD_FILENAME, ' ', fname).strip()
        save_to = path / fname
        if save_to.exists():
            continue
        print('#%02d Downloading %s...' % (tid, fname))
        resp = requests.get(url)
        with save_to.open('wb') as f:
            f.write(resp.content)
        queue.task_done()
    print('#%02d exited.' % tid)


def main():
    if not 2 <= len(sys.argv) <= 3:
        print('Download all images from rule34.paheal.net, ignore existing '
              'files.\n')
        print('Usage: %s <keyword> [threads-num]' % sys.argv[0])
        sys.exit(1)
    kw = sys.argv[1]
    if len(sys.argv) >= 3:
        thread_num = int(sys.argv[2])
    else:
        thread_num = DOWNLOAD_THREAD
    
    path = Path(kw)
    if not path.exists():
        path.mkdir()
    elif not path.is_dir():
        print('Cannot wirte to %s, file exists.' % path)

    print('Fetching the number of pages...')
    pages = fetch_total_pages(kw)
    print('%s page(s) in total.' % pages)

    queue = Queue(thread_num * 20)
    threads = []
    for i in range(thread_num):
        t = Thread(target=download, args=(queue, path, i))
        t.start()
        threads.append(t)
    print('%s threads are ready.' % len(threads))

    for url in fetch_urls(kw, 1, pages):
        queue.put(url)

    for i in range(len(threads)):
        queue.put(None)
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()