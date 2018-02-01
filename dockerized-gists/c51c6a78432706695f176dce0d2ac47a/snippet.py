import sqlite3
from contextlib import closing
import multiprocessing

def prepare_db(db, tbl, col):
    sql = "CREATE TABLE {0} ({1} text);".format(tbl, col)
    with closing(sqlite3.connect(db)) as cnn:
        cursor = cnn.cursor()
        cursor.execute('DROP TABLE IF EXISTS {0};'.format(tbl))
        cursor.execute(sql)
        cnn.commit()
    return db, tbl, col

def write(db, tbl, col, value):

    # have to set the timeout reasonably high, otherwise "database is locked"
    timeout = 20.0

    with closing(sqlite3.connect(db, timeout=timeout)) as cnn:
        cursor = cnn.cursor()
        cursor.execute("INSERT INTO {0} ({1}) VALUES ('{2}');".format(tbl, col, value))
        cnn.commit()

def work(d):
    db = r'c:\temp\multi.sqlite'
    tbl = 'logging'
    col = 'logged'

    write(db, tbl, col, d)

    return d

def main():
    data = list(range(100))

    db = r'c:\temp\multi.sqlite'
    tbl = 'logging'
    col = 'logged'

    prepare_db(db, tbl, col)

    pool = multiprocessing.Pool(4)

    mapped = pool.map(work, data)

    pool.close()
    pool.join()

    return mapped

if __name__ == "__main__":
    main()
