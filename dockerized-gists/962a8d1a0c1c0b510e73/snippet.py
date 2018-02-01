#!/usr/bin/python

import sys
import csv
import time

"""
PyCDR.py

Author: Steve Campbell, Github: https://github.com/sdcampbell/PyCDR

Purpose: Searches the Cisco Call Manager (CUCM) Call Detail Records (CDR) csv file for an extension,
and saves the Date/Time, call duration, calling number, and called number to a new csv file.

Directions: Download the CDR from https://<cucmserver>/ccmservice/, select the date range,
and DO NOT CHECK 'CMR RECORDS'!
Run this script and specify three command line arguments:
1. The path and name of the input csv file
2. The path and name of the output csv file
3. The extension to search for

Example: PyCDR.py "/path/to/cdr.txt" "/path/to/output.txt" 4357
"""


def date_and_time(time_value):
    return time.strftime("%m/%d/%y %H:%M:%S", time.localtime(float(time_value)))

def convert_duration(secs):
    secs = int(secs)
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':

    usage = 'Error, Correct Usage: PyCDR.py "/path/to/cdrfile" "/path/to/output.txt" 4357'

    if (len(sys.argv) < 4):
        print(usage)
        sys.exit()

    else:
        infile = open((sys.argv[1]), 'r')
        outfile = open((sys.argv[2]), 'w')
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        writer.writerow(['Date/Time', 'Duration', 'Calling Number', 'Called Number'] )

        for row in reader:
            if row[8] == (sys.argv[3]) or row[29] == (sys.argv[3]):
                writer.writerow([date_and_time(row[47]),convert_duration(row[55]),row[8],row[29]])

        print("Finished successfully!")
        infile.close()
        outfile.close()
