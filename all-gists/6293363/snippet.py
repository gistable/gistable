#!/usr/bin/env python

import argparse
import sqlite3
import csv
import gzip
import bz2
import datetime

def prepare_database(conn):
    """
    
    Arguments:
    - `conn`:
    """
    conn.execute('CREATE TABLE IF NOT EXISTS access (remote TEXT, user TEXT, date DATETIME, request TEXT, status TEXT, size INTEGER, referrer TEXT, useragent TEXT)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__remote ON access(remote)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__user ON access(user)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__date ON access(date)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__request ON access(request)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__status ON access(status)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__size ON access(size)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__referrer ON access(referrer)')
    conn.execute('CREATE INDEX IF NOT EXISTS access__useragent ON access(useragent)')

def import_log(conn, fileobj):
    """
    
    Arguments:
    - `conn`:
    - `fileobj`:
    """

    reader = csv.reader(fileobj, quotechar='"', delimiter=' ')
    for row in reader:
        #print row
        date = datetime.datetime.strptime(row[3], '[%d/%b/%Y:%H:%M:%S')
        conn.execute('INSERT INTO access VALUES(?, ?, ?, ?, ?, ?, ?, ?)', [row[0]]+[row[2]]+[date] + row[5:])

def open_compressed(path):
    """
    
    Arguments:
    - `path`:
    """

    if path.endswith('.gz'):
        return gzip.open(path, 'r')
    if path.endswith('.bz2'):
        return bz2.open(path, 'r')
    return open(path, 'r')


def _main():
    parser = argparse.ArgumentParser(description="Apache log to sqlite3")
    parser.add_argument('apachelog', nargs='+')
    parser.add_argument('-d', '--sqlitedb', required=True)
    options = parser.parse_args()

    conn = sqlite3.connect(options.sqlitedb)
    prepare_database(conn)
    for i in options.apachelog:
        f = open_compressed(i)
        import_log(conn, f)
        f.close()
    conn.commit()
    
if __name__ == '__main__':
    _main()
