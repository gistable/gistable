#coding:utf-8

import os
import time
from multiprocessing import Process
import pymongo

def print_tweet(collection):
    db = pymongo.Connection().twitter
    pid = os.getpid()
    for row in db[collection].find():
        if 'text' in row:
            print pid, row['text']

def multiprocess(collections):
    # mongodbのコレクションの数だけprocessを生成する
    lst = []
    for collection in collections:
        lst.append(Process(target=print_tweet, args=(collection,)))
    for t in lst:
        t.start()
    for t in lst:
        t.join()

def singleprocess(collections):
    db = pymongo.Connection().twitter
    pid = os.getpid()
    for collection in collections:
        for row in db[collection].find():
            if 'text' in row:
                print pid, row['text']

if __name__ == '__main__':
    collections = ['sample20111130', 'sample20111201', 'sample20111202', 'sample20111203']

    single_start = time.time()
    singleprocess(collections)
    single_sec = time.time() - single_start

    multi_start = time.time()
    multiprocess(collections)
    multi_sec = time.time() - multi_start

    print 'multiprocess', multi_sec
    print 'singleprocess', single_sec

    # multiprocess 25.4185650349
    # singleprocess 57.7358958721
