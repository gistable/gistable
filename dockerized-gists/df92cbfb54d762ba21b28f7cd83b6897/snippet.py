#!/usr/bin/env python

# fix-metadata-values.py
#
# Expects a CSV with two columns: one with "bad" metadata values and one with
# correct values. Basically just a mass search and replace function for DSpace's
# PostgreSQL database. Make sure to do a full `index-discovery -b` afterwards.
#
# TODO:
#   - write better help for required options
#   - dry run mode? Start transaction and roll it back?
#
# The script is written for Python 3+ and requires PETL and Psycopg2:
#
#   $ pip install petl psycopg2
#
# See: https://petl.readthedocs.org/en/latest
# See: http://initd.org/psycopg
# See: http://initd.org/psycopg/docs/usage.html#with-statement
# See: http://initd.org/psycopg/docs/faq.html#best-practices
#
# Alan Orth
# June, 2016

import petl as etl
import os.path
import subprocess
import sys
import signal
import psycopg2
import argparse

def signal_handler(signal, frame):
    sys.exit(0)

####### MAIN ######

parser = argparse.ArgumentParser(description="Find and replace metadata values in the DSpace SQL database.")
parser.add_argument("--from-field-name", "-f", help="Name of column with values to be replaced")
parser.add_argument("--to-field-name", "-t", help="Name of column with values to replace")
parser.add_argument("--metadata-field-id", "-m", type=int, help="ID of the field in the metadatafieldregistry table")
parser.add_argument("--csv-file", "-i", help="Path to CSV file")
parser.add_argument("--database-name", "-d", help="Database name")
parser.add_argument("--database-user", "-u", help="Database username")
parser.add_argument("--database-pass", "-p", help="Database password")
args = parser.parse_args()

# make sure the user passed the mandatory parameters
if all((args.from_field_name, args.to_field_name, args.metadata_field_id, args.csv_file)):
    records = etl.fromcsv(args.csv_file)
else:
    print("You must specify at least -f, -i, -m, and -t. See --help for details.")
    exit()

# set the signal handler for SIGINT (^C)
signal.signal(signal.SIGINT, signal_handler)

# connect to database
try:
    # if the user provided a database password
    if args.database_pass:
        conn = psycopg2.connect("dbname={} user={} password={} host='localhost'".format(args.database_name, args.database_user, args.database_pass))
    # otherwise, connect without a password
    else:
        conn = psycopg2.connect("dbname={} user={} host='localhost'".format(args.database_name, args.database_user))
except:
    print("Unable to connect to the database")
    exit()

# get these fields from the CSV
for record in etl.values(records, args.from_field_name, args.to_field_name):
    with conn:
        with conn.cursor() as curs:
            # resource_type_id 2 is metadata for items
            sql = "SELECT text_value FROM metadatavalue WHERE resource_type_id=2 AND metadata_field_id=%s AND text_value=%s"
            curs.execute(sql, (args.metadata_field_id, record[0]))
            records_to_fix = curs.rowcount

    print("Fixing {} occurences of: {}".format(records_to_fix, record[0]))

    with conn:
        with conn.cursor() as curs:
            sql = "UPDATE metadatavalue SET text_value=%s WHERE resource_type_id=2 AND metadata_field_id=%s AND text_value=%s"
            curs.execute(sql, (record[1], args.metadata_field_id, record[0]))
            rows_updated = curs.rowcount
            print("> {} occurences updated".format(rows_updated))