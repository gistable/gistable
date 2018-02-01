#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request
import html.parser
import xml.etree.ElementTree
import queue
import threading
import functools
import os
import sys
import time

RSS_CACHE = 'cache.rss'
EXPIRED_SECONDS = 3600
MAIN_THREADS_LIMITED = 4
SUB_THREADS_LIMITED = 2

def fetch_page(url, char_encoding = 'utf-8'):
    req = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        pass
    else:
        return response.read().decode(char_encoding, 'strict')

class ContentParser(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.handle_flag = 0
    def handle_starttag(self, tag, attrs):
        if self.handle_flag == 1:
            if tag == 'div':
                for attr in attrs:
                    if attr[0] == 'class':
                        if attr[1] == 'wumii-hook':
                            self.handle_flag = 0
                        break
                if self.handle_flag == 1:
                    self.handle_content.append(self.get_starttag_text())
            else:
                self.handle_content.append(self.get_starttag_text())
        else:
            if tag == 'div':
                for attr in attrs:
                    if attr[0] == 'class':
                        if attr[1] == 'entry':
                            self.handle_flag = 1
                            self.handle_content = []
                        break
    def handle_endtag(self, tag):
        if self.handle_flag == 1:
            self.handle_content.append('</{0}>'.format(tag))
    def handle_startendtag(self, tag, attrs):
        if self.handle_flag == 1:
            self.handle_content.append(self.get_starttag_text())
    def handle_data(self, data):
        if self.handle_flag == 1:
            self.handle_content.append(data)

class LinksParser(html.parser.HTMLParser):
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.handle_pagebar_flag = 0
        self.handle_depth = 0
    def handle_starttag(self, tag, attrs):
        if self.handle_pagebar_flag == 0:
            if tag == 'div':
                for attr in attrs:
                    if attr[0] == 'class' and attr[1] == 'pagebar':
                        self.handle_pagebar_flag = 1
                        self.handle_links = []
                        self.handle_depth += 1
                        break
        else:
            self.handle_depth += 1
            if tag == 'a':
                for attr in attrs:
                    if attr[0] == 'href':
                        self.handle_links.append(attr[1])
                        break
    def handle_endtag(self, tag):
        if self.handle_pagebar_flag == 1:
            self.handle_depth -= 1
            if self.handle_depth == 0:
                self.handle_pagebar_flag = 0
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_data(self, data):
        pass

class ThreadMainItem(threading.Thread):
    def __init__(self, queue, result):
        threading.Thread.__init__(self)
        self.queue = queue
        self.result = result
        self.page_parser = ContentParser()
        self.pagelinks_parser = LinksParser()
    def run(self):
        while True:
            item_array = self.queue.get()
            item_id = item_array[0]
            item_link = item_array[1]
            #print("{0} gets main {1} {2}".format(self.name, item_id, item_link))
            page = fetch_page(item_link)
            self.pagelinks_parser.feed(page)
            self.pagelinks_parser.close()
            self.page_parser.feed(page)
            links = self.pagelinks_parser.handle_links
            self.page_parser.close()
            links_len = len(links)
            sub_result = [None]*(links_len + 1)
            sub_result[0] = ''.join(self.page_parser.handle_content)
            if links_len > 0:
                sub_queue = queue.Queue()
                sub_threads = []
                for i in range(0, SUB_THREADS_LIMITED):
                    t = ThreadSubItem(sub_queue, sub_result)
                    t.daemon = True
                    t.start()
                    sub_threads.append(t)
                i = 1
                for link in links:
                    sub_queue.put((i, link))
                    i += 1
                sub_queue.join()
                #print("Sub Queue Finished!")
            self.result[item_id] = sub_result
            self.queue.task_done()
            #print("{0} finished main {1} {2}".format(self.name, item_id, item_link))

class ThreadSubItem(threading.Thread):
    def __init__(self, queue, result):
        threading.Thread.__init__(self)
        self.queue = queue
        self.result = result
        self.page_parser = ContentParser()
    def run(self):
        while True:
            subitem_array = self.queue.get()
            subitem_id = subitem_array[0]
            subitem_link = subitem_array[1]
            #print("{0} gets sub {1} {2}".format(self.name, subitem_id, subitem_link))
            self.page_parser.feed(fetch_page(subitem_link))
            self.result[subitem_id] = ''.join(self.page_parser.handle_content)
            self.page_parser.close()
            self.queue.task_done()
            #print("{0} finished sub {1} {2}".format(self.name, subitem_id, subitem_link))

def print_time(fgcolor = 'red', bgcolor = 'black'):
    color_array = {
            'black': ('30', '40'),
            'red': ('31', '41'),
            'green': ('32', '42'),
            'yellow': ('33', '43'),
            'blue': ('34', '44'),
            'magenta': ('35', '45'),
            'cyan': ('36', '46'),
            'white': ('37', '47')
            }
    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            stdout = sys.stdout
            with open(os.devnull, 'w') as f:
                sys.stdout = f
                start = time.time()
                result = func(*args, **kwargs)
                end = time.time()
            sys.stdout = stdout
            print('\033[{0};{1};1mdelta time: {2}\033[0m'.format(color_array[fgcolor][0], color_array[bgcolor][1], str(end - start)))
            return result
        return _wrapper
    return _decorator

#@print_time()
def main():
    if os.path.isfile(RSS_CACHE) and os.stat(RSS_CACHE).st_mtime + EXPIRED_SECONDS > time.time():
        with open(RSS_CACHE, 'rb') as cache:
            while True:
                cache_data = cache.read()
                if cache_data:
                    sys.stdout.buffer.write(cache_data)
                else:
                    break
    else:
        rss = fetch_page('http://www.hexieshe.com/feed/')
        #rss = fetch_page('http://127.0.0.1/~jahiy/hxs.xml')
        root = xml.etree.ElementTree.XML(rss)
        main_queue = queue.Queue()
        items = root[0].findall('item')
        result = [None]*len(items)
        threads = []
        for i in range(0, MAIN_THREADS_LIMITED):
            t = ThreadMainItem(main_queue, result)
            t.daemon = True
            t.start()
            threads.append(t)
        i = 0
        for item in items:
            main_queue.put((i, item.find('link').text))
            #print("Main Queue put {0} {1}".format(i, item.find('link').text))
            i += 1
        main_queue.join()
        #print("Main Queue Finished!")
        for item, content in zip(items, result):
            item.find('description').text = ''.join(content)
        fullfeed = xml.etree.ElementTree.tostring(root, 'utf-8')
        with open(RSS_CACHE, 'wb') as cache:
            cache.write(fullfeed)
        sys.stdout.buffer.write(fullfeed)
    return 0

if __name__ == '__main__':
    sys.stdout.buffer.write('Content-type: text/xml;charset=utf-8\n\n'.encode('utf-8'))
    main()