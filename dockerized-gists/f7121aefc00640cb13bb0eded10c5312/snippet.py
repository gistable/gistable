# -*- coding=utf-8 -*-
import Queue
import functools
import logging
import os
import re
import sys
import time
from functools import partial
from itertools import repeat
from multiprocessing import Pool, cpu_count, freeze_support
from threading import Thread

import requests
from retry import retry
from tqdm import tqdm

api_url = 'http://%s.tumblr.com/api/read?&num=50&start='
UQueue = Queue.Queue()


def getpost(uid, queue):
    url = 'http://%s.tumblr.com/api/read?&num=50' % uid
    page = requests.get(url).content
    total = re.findall('<posts start="0" total="(.*?)">', page)[0]
    total = int(total)
    a = [i * 50 for i in range(1000) if i * 50 - total < 0]
    ul = api_url % uid
    for i in a:
        queue.put(ul + str(i))


# search for url of maxium size of a picture, which starts with
# '<photo-url max-width="1280">' and ends with '</photo-url>'
extractpicre = re.compile(
    r'(?<=<photo-url max-width="1280">).+?(?=</photo-url>)', flags=re.S)
extractvideore = re.compile('/tumblr_(.*?)" type="video/mp4"')

video_links = []
pic_links = []
vhead = 'https://vt.tumblr.com/tumblr_%s.mp4'


class Consumer(Thread):
    def __init__(self, l_queue):
        super(Consumer, self).__init__()
        self.queue = l_queue

    def run(self):
        session = requests.Session()
        while 1:
            link = self.queue.get()
            print 'start parse post: ' + link
            try:
                content = session.get(link).content
                videos = extractvideore.findall(content)
                video_links.extend([vhead % v for v in videos])
                pic_links.extend(extractpicre.findall(content))
            except:
                print 'url: %s parse failed\n' % link
            if self.queue.empty():
                break


def main():
    task = []
    for i in range(min(10, UQueue.qsize())):
        t = Consumer(UQueue)
        task.append(t)
    for t in task:
        t.start()
    for t in task:
        t.join
    while 1:
        for t in task:
            if t.is_alive():
                continue
            else:
                task.remove(t)
        if len(task) == 0:
            break


def write():
    videos = [i.replace('/480', '') for i in video_links]
    pictures = pic_links
    videos = list(set(videos))
    pictures = list(set(pictures))
    with open('pictures.txt', 'w') as f:
        for i in pictures:
            f.write('%s\n' % i)
    with open('videos.txt', 'w') as f:
        for i in videos:
            f.write('%s\n' % i)


class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)


@retry(tries=3, delay=2)
def download(url, local_filename=None, proxies=None, root_dir=None, if_exist='ignore'):
    if not local_filename:
        local_filename = url.split('/')[-1]
    if root_dir:
        local_filename = os.path.join(root_dir, local_filename)
    if os.path.exists(local_filename) and if_exist == 'ignore':
        return None
    try:
        r = requests.get(url, proxies=proxies, stream=True)
        if r.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=4096):
                    if chunk:
                        f.write(chunk)
            print "finish download %s" % local_filename
            time.sleep(.5)
        else:
            raise Exception("Unexpected response.")
    except requests.exceptions.RequestException as e:
        raise
    except Exception as e:
        raise


if __name__ == '__main__':
    freeze_support()  # for Windows support
    # name=sys.argv[1]
    # name=name.strip()
    name = 'wanimal1983'
    getpost(name, UQueue)
    main()
    write()
    with open('pictures.txt', 'r') as f:
        urls = [url.strip() for url in f.readlines()]

    if not os.path.exists(name):
        os.mkdir(name)

    pool = Pool(cpu_count())
    download_base_dir = partial(download, root_dir=name)
    pool = Pool()
    try:
        for square in tqdm(pool.imap_unordered(download_base_dir, urls), total=len(urls)):
            pass
    except KeyboardInterrupt:
        logging.warning("got Ctrl+C")
    finally:
        pool.terminate()
        pool.join()
