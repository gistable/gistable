#!/usr/bin/env python

'''
pip install pysqlite
pip install unqlite
'''

import sqlite3
from unqlite import UnQLite
import timeit
import os


def create_sqlite_table():
    conn = sqlite3.connect('tmp.sqlite3')
    c = conn.cursor()
    c.execute(
        '''
        create table test_table
        (a text, b text, c text)
        '''
    )
    conn.close()


def insert_sqlite_rows(number):
    conn = sqlite3.connect('tmp.sqlite3')
    c = conn.cursor()
    for x in xrange(number):
        c.execute(
            '''
            insert into test_table values(?,'2','3')
            ''',
            [x]
        )
        conn.commit()
    conn.close()


def insert_unqlite_items(number):
    db = UnQLite('tmp.unqlite')
    items = db.collection('items')
    items.create()
    for x in xrange(number):
        items.store([{
            'a': str(x),
            'b': '2',
            'c': '3',
        }])


if __name__ == '__main__':
    os.unlink('tmp.unqlite')
    os.unlink('tmp.sqlite3')
    create_sqlite_table()
    print "insert_sqlite_rows(1000):   ", timeit.timeit("insert_sqlite_rows(1000)", setup="from __main__ import insert_sqlite_rows", number=1)
    print "insert_unqlite_items(1000): ", timeit.timeit("insert_unqlite_items(1000)", setup="from __main__ import insert_unqlite_items", number=1)
    print 'sqlite size:  ', os.path.getsize('tmp.sqlite3')
    print 'unqlite size: ', os.path.getsize('tmp.unqlite')
