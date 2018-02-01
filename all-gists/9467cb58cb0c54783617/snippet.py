#!/usr/bin/env python
import argparse
import psycopg2
import psycopg2.extras
import csv
from getpass import getpass, getuser

def main(args):
    '''
    Inserts a TSV into table in postgresql
    ingest_psotgresql.py <input> [-i host[:port]] [-u username[:pass]] <database> <table>
    '''
    params = {}
    params['host'] = args.host
    params['dbname'] = args.database
    username = args.user or getuser()
    if ':' in username:
        username, password = username.split(':')
    else:
        password = None

    params['user'] = username
    params['password'] = password
    params['tries'] = 0
    conn = try_connect(params)
    insert_file(args.input, args.table, conn)

    conn.close()

def build_conn_string(params):
    '''
    Builds the postgresql connection string
    '''
    conn_string = "host='%(host)s' dbname='%(dbname)s' user='%(user)s'" % params
    if params['password']:
        conn_string += " password='%(password)s'" % params
    return conn_string

def try_connect(params, prompt_password=False):
    '''
    Attempts a connection with the database
    '''
    if prompt_password:
        password = getpass()
        params['password'] = password

    conn_string = build_conn_string(params)

    try:
        conn = psycopg2.connect(conn_string)

    except psycopg2.OperationalError as e:
        if 'password authentication failed' in e.message:
            if params['tries'] > 1:
                print e.message
            if params['tries'] > 2:
                raise
            params['tries'] += 1
            conn = try_connect(params, prompt_password=True)

        raise

    return conn


def insert_file(filename, tablename, conn):
    '''
    '''
    cursor = conn.cursor()

    sql = 'DROP TABLE IF EXISTS tmp';
    cursor.execute(sql)

    sql = 'CREATE TEMP TABLE tmp AS SELECT * FROM %s LIMIT 0' % tablename
    cursor.execute(sql)


    with open(filename, 'rU') as tsv:
        tsvreader = csv.reader(tsv, delimiter='\t')
        headers = tsvreader.next()
        for row in tsvreader:
            sql = 'INSERT INTO tmp (%s) VALUES (%s)' % (', '.join(headers), ', '.join('%s' for col in row))
            row = [r if r != '' else None for r in row]
            cursor.execute(sql, row)

    conn.commit()

    non_id_headers = [col for col in headers if col != 'id']

    sql = '''
INSERT INTO %s (%s) (
    SELECT %s FROM tmp WHERE id IS NULL
);''' % (tablename, ', '.join(non_id_headers), ', '.join(non_id_headers))
    cursor.execute(sql)

    sql = 'UPDATE %s SET %s FROM tmp WHERE %s.id=tmp.id AND tmp.id IS NOT NULL' % (tablename, ', '.join(['%s=tmp.%s' % (h,h) for h in non_id_headers]), tablename)
    cursor.execute(sql)

    sql = 'DROP TABLE tmp'
    cursor.execute(sql)
    conn.commit()
            



if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False, description=main.__doc__)
    parser.add_argument('input', help='Input TSV file')
    parser.add_argument('-h', '--host', type=str, default='localhost', help='hostname and optionally port')
    parser.add_argument('-u', '--user', type=str, help='username and optionally password')
    parser.add_argument('database', help='Databse Name')
    parser.add_argument('table', help='Table name')
    args = parser.parse_args()
    main(args)

