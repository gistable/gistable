#!/usr/bin/env python
"""
simple mssql -> csv file example using pymssql
@author jack@tinybike.net
"""
import csv
import datetime
import pymssql
from decimal import Decimal

# Connect to MSSQL Server
conn = pymssql.connect(server="SERVER:PORT",
                       user="USERNAME",
                       password="PASSWORD",
                       database="DATABASE")

# Create a database cursor
cursor = conn.cursor()

# Replace this nonsense with your own query :)
query = """SELECT TOP 25 * FROM FSDBDATA.dbo.MS04311
WHERE sitecode LIKE 'PRIMET'
ORDER BY DATE_TIME DESC"""

# Execute the query
cursor.execute(query)

# Go through the results row-by-row and write the output to a CSV file
# (QUOTE_NONNUMERIC applies quotes to non-numeric data; change this to
# QUOTE_NONE for no quotes.  See https://docs.python.org/2/library/csv.html
# for other settings options)
with open("output.csv", "w") as outfile:
    writer = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)
    for row in cursor:
        writer.writerow(row)

# Close the cursor and the database connection
cursor.close()
conn.close()
