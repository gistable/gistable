#!/usr/bin/env python
# -*- encoding: UTF8 -*-

""" Store all entered bash commands ('the history') in a database
http://blog.philippklaus.de/2015/04/enhancing-and-enlarging-the-bash-history/
"""

import sqlite3
from os import path, makedirs
import sys
from datetime import datetime

__author__ = "Philipp Klaus"
__copyright__ = "Copyright 2015 Philipp Klaus"
__credits__ = ""
__license__ = "GPL"
__version__ = "2.0"
__maintainer__= ""
__email__ = "philipp.klaus AT gmail.com"
__status__ = "Development" # Prototype Production

DATABASE_FILE = path.expanduser('~/.histToDB/histToDB.sqlite')

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Hist to DB')
    parser.add_argument('--print', action='store_true', help='Print the hist instead of writing it')
    args = parser.parse_args()

    connect_db()

    if vars(args)['print']:
        print_all_datasets()
        sys.exit(0)

    time = 0
    command = ''
    for line in open(path.expanduser('~/.bash_history'),'r'):
        line = line.strip()
        if len(line)>0 and line[0]=='#':
            try:
                time = datetime.fromtimestamp(int(line.replace("#","")))
            except:
                time = 0
        elif time != 0:
            command = line
            if not already_in_db((time,)):
                print("Adding ({},{})".format(time, command))
                # as long as we have got a UTF8 terminal
                # in future check os.environ['LANG'] to derive encoding...
                insert_history_row((time,unicode(command,"utf-8")))
            else:
                print("NOT adding ({},{})".format(time, command))
            time = 0

def create_initial_database(db):
    curs = db.cursor()
    curs.execute('CREATE TABLE bash_history (time TIMESTAMP PRIMARY KEY, command TEXT)')
    db.commit()
    return db


def connect_db():
    try:
        open(DATABASE_FILE)
        db = sqlite3.connect(DATABASE_FILE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    except:
        if not path.exists(path.split(DATABASE_FILE)[0]):
            makedirs(path.split(DATABASE_FILE)[0])
        db = sqlite3.connect(DATABASE_FILE, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        create_initial_database(db)
        print("created inital database.")
    # "detect_...": to use the default adapters for datetime.date and datetime.datetime see http://docs.python.org/library/sqlite3.html#default-adapters-and-converters
    return db


def insert_history_row(history):
    conn = connect_db()
    curs = conn.cursor()
    curs.execute('INSERT INTO bash_history VALUES (?,?)',history)
    conn.commit()


def delete_db():
    try:
        remove(DATABASE_FILE)
    except:
        print("error while trying to delete sqlite database " + DATABASE_FILE)

def get_all_datasets():
    curs = connect_db().cursor()
    curs.execute('SELECT * from bash_history LIMIT 1000000')
    return curs

def already_in_db(key):
    curs = connect_db().cursor()
    curs.execute('SELECT count(*) from bash_history WHERE time=?',key)
    return curs.fetchone()[0] > 0

def print_all_datasets():
    for ds in get_all_datasets():
        print "%s %s" % ds

if __name__ == "__main__":
    main()
