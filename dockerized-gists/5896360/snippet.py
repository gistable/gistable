#!/usr/bin/env python
#vim: encoding=utf-8

"""
Backup my google reader records.

Usage:
  $ pip install libgreader python-daemon pony
  $ python myreader.py
  
Your data will save to `myreader.sqlite` file.
"""

import sys
import socket
from datetime import datetime
from multiprocessing import Process

import daemon
from pony.orm import *
from libgreader import GoogleReader, ClientAuthMethod
socket.setdefaulttimeout(360)

db = Database("sqlite", "myreader.sqlite", create_db=True)

class Feed(db.Entity):
    title = Required(unicode, 1500, nullable=True)
    url = Optional(unicode, 1500, nullable=True)
    date_updated = Optional(datetime, nullable=True)
    items = Set("Item")

class Item(db.Entity):
    author = Optional(unicode, nullable=True)
    content = Optional(LongUnicode, lazy=True, nullable=True)
    title = Optional(unicode, 1500, nullable=True)
    date_created = Optional(datetime, nullable=True)
    url = Optional(unicode, 1500, nullable=True)
    isread = Optional(bool, default=False)
    isstarred = Optional(bool, nullable=True)
    isshared = Optional(bool, nullable=True)
    feed = Required(Feed)

#sql_debug(True)
db.generate_mapping(create_tables=True)

GMAIL_ACCOUNT = "YOUR_GOOGLE_READER_ACCOUNT"
GMAIL_PASSWORD = "AND_PASSWORD"

auth = ClientAuthMethod(GMAIL_ACCOUNT, GMAIL_PASSWORD)
reader = GoogleReader(auth)
reader.buildSubscriptionList()
categories = reader.categories
feeds = [c.getFeeds() for c in categories]

def fetch():
    for cate in reader.categories:
        #c = [i for i in reader.categories if i.label == "IT.JIE"][0]
        for cfeeds in feeds:
            for n, i in enumerate(cfeeds):
                p = Process(target=w, args=(cate, i))
                p.start()
                p.join()
                p.terminate()

def w(cate, feed, continuation=None, wmax=3000):
    print feed.title.encode("u8")
    count = 0
    
    ifeed = None
    with db_session:
        ifeed = select(i for i in Feed if i.title == feed.title).first()
        if ifeed is None:
            ifeed = Feed(
                title=feed.title,
                date_updated=datetime.fromtimestamp(feed.lastUpdated or 0),
                url=feed.feedUrl
            )

        feed.continuation = continuation
        if feed.continuation is None:
            feed.loadItems(loadLimit=1000)

        while feed.continuation:
            feed.loadMoreItems(loadLimit=1000)
            count += len(feed.items)
            print count
            for item in feed.items:
                Item(
                    author = item.author or u"",
                    content = item.content,
                    title = item.title,
                    date_created = datetime.fromtimestamp(item.data.get("published", 0)),
                    url = item.url,
                    isread = item.isRead(),
                    isstarred = item.isStarred(),
                    isshared = item.isShared(),
                    feed = ifeed
                )

            del feed.items
            feed.items = []

        if feed.items:
            for item in feed.items:
                Item(
                    author = item.author or u"",
                    content = item.content or u"",
                    title = item.title or u"",
                    date_created = datetime.fromtimestamp(item.data.get("published", 0)),
                    url = item.url or u"",
                    isread = item.isRead(),
                    isstarred = item.isStarred(),
                    isshared = item.isShared(),
                    feed = ifeed
                )
    sys.exit(0)

if __name__ == "__main__":
    fetch()