#!/usr/bin/env python

"""
Insert data into HBase with a Python script.

To create the table, first use the hbase shell. We are going to create a
namespace called "sample_data". The table for this script is called "rfic",
as we will be inserting Request for Information Cases from the City of
Indianapolis.

Our table will have only one column family named "data", and we are accepting
all table defaults.

Original data source
https://data.indy.gov/dataset/Request-for-Information-Cases/ts4b-8qa9

% hbase shell
hbase> create_namespace "sample_data"
hbase> create "sample_data:rfic", "data"
"""

import csv
import happybase
import time

batch_size = 1000
host = "0.0.0.0"
file_path = "Request_for_Information_Cases.csv"
namespace = "sample_data"
row_count = 0
start_time = time.time()
table_name = "rfic"


def connect_to_hbase():
    """ Connect to HBase server.

    This will use the host, namespace, table name, and batch size as defined in
    the global variables above.
    """
    conn = happybase.Connection(host = host,
        table_prefix = namespace,
        table_prefix_separator = ":")
    conn.open()
    table = conn.table(table_name)
    batch = table.batch(batch_size = batch_size)
    return conn, batch


def insert_row(batch, row):
    """ Insert a row into HBase.

    Write the row to the batch. When the batch size is reached, rows will be
    sent to the database.

    Rows have the following schema:
        [ id, keyword, subcategory, type, township, city, zip, council_district,
          opened, closed, status, origin, location ]
    """
    batch.put(row[0], { "data:kw": row[1], "data:sub": row[2], "data:type": row[3],
        "data:town": row[4], "data:city": row[5], "data:zip": row[6],
        "data:cdist": row[7], "data:open": row[8], "data:close": row[9],
        "data:status": row[10], "data:origin": row[11], "data:loc": row[12] })


def read_csv():
    csvfile = open(file_path, "r")
    csvreader = csv.reader(csvfile)
    return csvreader, csvfile


# After everything has been defined, run the script.
conn, batch = connect_to_hbase()
print "Connect to HBase. table name: %s, batch size: %i" % (table_name, batch_size)
csvreader, csvfile = read_csv()
print "Connected to file. name: %s" % (file_path)

try:
    # Loop through the rows. The first row contains column headers, so skip that
    # row. Insert all remaining rows into the database.
    for row in csvreader:
        row_count += 1
        if row_count == 1:
            pass
        else:
            insert_row(batch, row)

    # If there are any leftover rows in the batch, send them now.
    batch.send()
finally:
    # No matter what happens, close the file handle.
    csvfile.close()
    conn.close()

duration = time.time() - start_time
print "Done. row count: %i, duration: %.3f s" % (row_count, duration)