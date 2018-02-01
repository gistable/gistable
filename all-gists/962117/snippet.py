#!/usr/bin/python

import os
import sys
from codecs import iterdecode
from zipfile import ZipFile
import csv
import datetime

if len(sys.argv) < 2:
    print "Usage: %prog <gtfs feed>"
    exit(1)

filename = sys.argv[1]

zf = ZipFile(filename)
contents = zf.read('calendar.txt')

rows = csv.reader(iterdecode( contents.split("\n"),"utf-8"))
header = rows.next()
headerdict = dict(zip(header, range(len(header)))) 

(min_start_date, max_end_date) = map(lambda ds: datetime.date(int(ds[0:4]),
                                                             int(ds[4:6]),
                                                             int(ds[6:8])),
                                     reduce(lambda x,y: (min(x[0],y[0]), 
                                                         max(x[1],y[1])),
                                            map(lambda x: (x[headerdict['start_date']],
                                                           x[headerdict['end_date']]), rows)))
print min_start_date
print max_end_date
