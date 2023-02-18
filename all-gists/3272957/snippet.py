#!/usr/bin/env python
import os
import argparse
import sqlite3
import logging

try:
    # tornado is bundled with pretty formatter - try using it
    from tornado.options import enable_pretty_logging
    enable_pretty_logging()
except:
    pass

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def sqlite_db(path):
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError('%s is not a file' % path)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    # test if this is really sqlite file
    cur = conn.cursor()
    cur.execute('SELECT 1 from sqlite_main where type = "table"')
    try:
        data = cur.fetchone()
    except sqlite3.DatabaseError:
        msg = '%s can\'t be read as SQLite DB' % path
        raise argparse.ArgumentTypeError(msg)

    return conn

parser = argparse.ArgumentParser(description='Merge data from src to dest db')
parser.add_argument('src_db', type=sqlite_db,
                    help='Source DB file path')
parser.add_argument('dst_db', type=sqlite_db,
                    help='Destination DB file path')

args = parser.parse_args()

src_cur = args.src_db.cursor()
dst_cur = args.dst_db.cursor()

src_cur.execute('SELECT * from sqlite_main')
src_main = src_cur.fetchall()

src_tables = filter(lambda r: r['type'] == 'table', src_main)
src_indices = filter(lambda r: r['type'] == 'index' and r['sql'] is not None, src_main)

logger.info('Found tables: %d', len(src_tables))
for table in src_tables:
    logger.info('Processing table: %s', table['name'])

    logger.info('Delete old table in destination db, if exists')
    dst_cur.execute("DROP TABLE IF EXISTS " + table['name'])

    logger.info('Creating table structure')
    logger.debug('SQL: %s', table['sql'])
    dst_cur.execute(table['sql'])

    logger.info('Moving data')
    src_cur.execute('SELECT COUNT(1) AS cnt FROM %s' % table['name'])
    total_rows = src_cur.fetchone()['cnt']
    logger.debug('Rows: %d', total_rows)

    src_cur.execute('SELECT * FROM %s' % table['name'])
    item = 0
    for row in src_cur:
        item += 1
        if item % 50000 == 0:
            logger.debug('Processing %d / %d', item, total_rows)
            args.dst_db.commit()

        cols = row.keys()
        query = 'INSERT INTO %(tbl)s (%(cols)s) VALUES (%(phold)s)' % {
            'tbl': table['name'],
            'cols': ','.join(cols),
            'phold': ','.join(('?',) * len(cols))
            }
        dst_cur.execute(query, [row[col] for col in cols])

    args.dst_db.commit()

    logger.info('Creating table indices')
    table_idx = filter(lambda r: r['tbl_name'] == table['name'], src_indices)
    logger.info('Found indices: %d', len(table_idx))
    for idx in table_idx:
        logger.debug('SQL: %s', idx['sql'])
        dst_cur.execute(idx['sql'])
    
    logger.info('Finished with %s', table['name'])

args.src_db.close()
args.dst_db.close()