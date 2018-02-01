#!/usr/bin/env python
"""
Script to open a sqlite3 database and dump all user tables to CSV files.
Tested in Unicode-rich environment.

Usage:
    dumpsqlite3tocsv foo.db
"""

import sqlite3, csv, codecs, cStringIO, os, os.path

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    Source: http://docs.python.org/library/csv.html#csv-examples
    Modified to cope with non-string columns.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def encodeone(self, item):
        if type(item) == unicode:
            return self.encoder.encode(item)
        else:
            return item

    def writerow(self, row):
        self.writer.writerow([self.encodeone(s) for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def dump_database_to_spreadsheets(filepath):
    db = sqlite3.connect('REF.db')
    shortname, extension = os.path.splitext(filepath)
    os.path.isdir(shortname) or os.mkdir(shortname)
    cursor = db.cursor()
    for table in list_tables(cursor):
        sheetfile = '%s.csv' % table
        sheetpath = os.path.join(shortname, sheetfile)
        dump_table_to_spreadsheet(cursor, table, sheetpath)

def list_tables(cursor):
    cursor.execute('select name from sqlite_master')
    return [r[0] for r in cursor
            if not r[0].startswith('sqlite')
            and not r[0].endswith('idx')]

def dump_table_to_spreadsheet(cursor, tablename, sheetpath):
    output = UnicodeWriter(file(sheetpath, 'w'))
    cursor.execute('select * from %s' % tablename)
    output.writerow([col[0] for col in cursor.description])
    filter(None, (output.writerow(row) for row in cursor))

if __name__ == '__main__':
    import sys
    for filepath in sys.argv[1:]:
        dump_database_to_spreadsheets(filepath)
