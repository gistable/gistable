#!/usr/bin/python
import psycopg2
import psycopg2.extras
from pyes import *
import argparse
import traceback
import math

def ResultIter(cursor, arraysize=100):
    # An iterator that uses fetchmany to keep memory usage down
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result

def PGDatabaseConn():
        try:
                conn = psycopg2.connect("dbname=" + args.db_name + " user=" + args.db_username + " host=" + args.db_host + " password=" + args.db_password)
        except:
                print "Unable to connect to postgres - host: %s" % args.db_host
                traceback.print_exc()
                exit(1)
        return conn.cursor('mycursor',cursor_factory=psycopg2.extras.RealDictCursor)

def ESConn():
        print "Conecting to elasticsearch"
        try:
                es = ES(args.es_host)
        except:
                print "Unable to connect to elasticsearch - host: %s" % args.es_host
                traceback.print_exc()
                exit(1)
        return es

def ESInsert(es, row):
        es.index(row, args.es_index, args.es_indextype)

parser = argparse.ArgumentParser(description='Convert postgres to elasticsearch')
parser.add_argument('-q','--query', required=True, help='Query to retrieve data')
parser.add_argument('--db_name', required=True, help='Postgres database name')
parser.add_argument('--db_username', required=True, help='Postgres database username')
parser.add_argument('--db_password', required=True, help='Postgres database password')
parser.add_argument('--db_host', required=True, help='Postgres host')
parser.add_argument('--es_host', required=True, help='Elastisearch host:port')
parser.add_argument('--es_index', required=True, help='Elastisearch index')
parser.add_argument('--es_indextype', required=True, help='Elastisearch index type')

args = parser.parse_args()

# Conn to PG and open a cursor
cur = PGDatabaseConn()

# Execute the query
print "Executing query -> %s" % args.query
cur.execute(args.query)

# Connect to elasticsearch
es = ESConn()

# Insert results
print "Inserting data into elasticsearch"
error=0
row_replace={}
for row in ResultIter(cur):
        try:
                ESInsert(es, row)
        except:
                try:
                        # Try replace float nan values to None
                        row_replace.clear()
                        row_replace.update(row)
                        for key,value in row.items():
                                if isinstance(value, float) and math.isnan(value):
                                        row_replace[key]=None
                        print row_replace
                        ESInsert(es, row_replace)
                except:
                        print "Error inserting row"
                        print row
                        error=1
                        traceback.print_exc()
                        continue

if error == 0:
        print "Done!!! :D "
        exit(0)
else:
        print "Done with errors  :( "
        exit(1)
