#!/usr/bin/env python3
# encoding: utf-8

"""
I saw a similar script on the homepage of Miguel Grinberg (the Flask book guy),
but he was using webscraping. Here I use simple API calls instead.

The script takes the presentations of a Python conference and orders the
presentations in descending order by the number of youtube views. It
is an indicator about the popularity of a video.

Usage:
    1) set the "conf" global variable
    2) launch the script

Requirements:
    pafy
    requests

Author:
    Laszlo Szathmary, alias Jabba Laci (jabba.laci@gmail.com)
    https://pythonadventures.wordpress.com/
"""

import concurrent.futures
import operator
import sys
from queue import Queue

import pafy
import requests

q = Queue()

#conf = "europython-2014"
#conf = "pycon-us-2014"
#conf = "pycon-us-2013"
#conf = "pycon-us-2012"
conf = "pycon-us-2015"
conf_url = "http://pyvideo.org/api/v2/category/{conf}?format=json".format(conf=conf)


class Video():
    def __init__(self, url):
        self.json_url = "{url}?format=json".format(url=url)
        r = requests.get(self.json_url)
        self.d = r.json()
        self.youtube_link = self.d["source_url"]
        self.process(self.youtube_link)

    def process(self, youtube_link):
        v = pafy.new(youtube_link)
        self.views = v.viewcount
        self.ups = v.likes
        self.downs = v.dislikes
        self.title = v.title
        self.speakers = ", ".join(self.d['speakers'])

    @staticmethod
    def header():
        return "{:>8} {:>6} {:>6}  {} ({})".format("Views", "Ups", "Downs", "Title", "Speakers")

    def __str__(self):
        return "{:8,} {:6,} {:6,}  {} ({})".format(self.views, self.ups, self.downs, self.title, self.speakers)


def process(video):
    v = Video(video)
    q.put(v)
    sys.stdout.write('.'); sys.stdout.flush()


def main():
    print(conf)
    #
    r = requests.get(conf_url)
    d = r.json()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for video in d['videos']:
            executor.submit(process, video)
    #
    print()
    li = []
    while not q.empty():
        li.append(q.get())
    #
    li.sort(key=operator.attrgetter("views"), reverse=True)
    print(Video.header())
    for e in li:
        print(e)

##############################################################################

if __name__ == "__main__":
    main()
