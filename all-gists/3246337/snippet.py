#!/usr/bin/env python

import sqlite3 as sqlite
import os
import sys
import time

# Extracts an mbtiles database into a pyramid structure

if len(sys.argv) != 2:
    print("No database specified")
    sys.exit(1)

if not os.path.exists(sys.argv[1]):
    print("No such database file {0}".format(sys.argv[1]))
    sys.exit(1)

dbfile = sys.argv[1]

if os.path.exists("tile_data"):
    os.rename("tile_data", "tile_data_" + str(time.time()))

os.mkdir("tile_data")
con = sqlite.connect(dbfile)

sql = "select zoom_level, tile_column, tile_row, tile_data from tiles"

cur = con.cursor()

for row in cur.execute(sql):

    if not os.path.exists("tile_data/{0}".format(row[0])):
        os.mkdir("tile_data/{0}".format(row[0]))

    if not os.path.exists("tile_data/{0}/{1}".format(row[0], row[1])):
        os.mkdir("tile_data/{0}/{1}".format(row[0], row[1]))

    imgData = open("tile_data/{0}/{1}/{2}.png".format(row[0], row[1], row[2]), 'w')
    imgData.write(row[3])
    imgData.close()

cur.close()

con.close()