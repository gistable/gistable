#!/usr/bin/env python
from __future__ import unicode_literals
import pymongo
import threading

DB_NAME = 'events'
COLLECTION_NAME = 'events'


class Subscriber(threading.Thread):

    def __init__(self, num):
        super(Subscriber, self).__init__()
        self.conn = pymongo.MongoClient()
        self.db = self.conn[DB_NAME]
        self.col = self.db[COLLECTION_NAME]
        self._stop = threading.Event()
        self.num = num

    def stop(self):
        self._stop.set()

    def run(self):
        cursor = self.col.find(tailable=True, await_data=True)
        while cursor.alive and not self._stop.isSet():
            try:
                record = cursor.next()
            except StopIteration:
                print self.num, 'waiting'
            else:
                print self.num, 'sub', record
        print self.num, 'done'


class Publisher(object):

    def __init__(self):
        super(Publisher, self).__init__()
        self.conn = pymongo.MongoClient()
        self.db = self.conn[DB_NAME]
        self.col = self.db[COLLECTION_NAME]

    def insert(self, data):
        print self.col.insert({
            'item': data,
        })


def main():
    conn = pymongo.MongoClient()
    db = conn[DB_NAME]
    db.drop_collection(COLLECTION_NAME)
    db.create_collection(COLLECTION_NAME, capped=True, size=100000)

    pub = Publisher()
    pub.insert('initial')

    threads = []
    for i in xrange(1):
        t = Subscriber(i)
        threads.append(t)
    for t in threads:
        t.start()
    while True:
        x = raw_input('What to insert? (q,quit)')
        if x in ['q', 'quit']:
            break
        pub.insert(x)
    for t in threads:
        t.stop()
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()
