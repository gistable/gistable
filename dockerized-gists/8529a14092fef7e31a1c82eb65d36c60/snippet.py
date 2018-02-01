import time
from random import randrange
import threading
import requests
from pymongo import MongoClient

some_database = MongoClient().some_database
some_collection = some_database.some_collection

def randhost():
    a = randrange(256)
    b = randrange(256)
    c = randrange(256)
    d = randrange(256)
    return '%i.%i.%i.%i' % (a, b, c, d)

def process(host, port):
    if port == 80:
        url = 'http://%s' % host
    elif port == 443:
        url = 'https://%s' % host
    else:
        url = 'http://%s:%i' % (host, port)
    req = requests.get(url, timeout=1)
    doc = {'host': host, 'port': port, 'headers': dict(req.headers)}
    some_collection.insert_one(doc)

def scanloop():
    while True:
        host = randhost()
        try:
            process(host, 80)
        except:
            pass

threadcount = 100

threads = []

for i in xrange(threadcount):
    thread = threading.Thread(target=scanloop)
    thread.daemon = True
    thread.start()
    threads.append(thread)

while threading.active_count() > 0:
    time.sleep(0.1)