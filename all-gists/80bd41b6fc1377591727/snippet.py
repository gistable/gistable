'''
What does it do?
Goes through a corrupted csv sequentially and outputs rows that are clean. 
Also outputs, total n, total corrupted n
    
@author: Gaurav Sood
Run: python salvage_csv.py input_csv output_csv

'''

import sys
import csv
csv.field_size_limit(sys.maxint)

if len(sys.argv) < 2:
    print("Usage: %s <input CSV> [<output CSV>]" % (sys.argv[0]))
    sys.exit()
o = None
if len(sys.argv) > 2:
    o = open(sys.argv[2], 'wb')

f = open(sys.argv[1])
reader = csv.reader(f)
if o is not None:
    writer = csv.writer(o)
ncols = 0
errors = 0
for i, r in enumerate(reader):
    if i == 0:
        ncols = len(r)
        print("Number of column: %d" % ncols)
        if o is not None:
            writer.writerow(r)
    else:
        if len(r) != ncols:
            print("WARN: row #%d is corrupted" % (i))
            errors += 1
        elif o is not None:
            writer.writerow(r)
f.close()
if o is not None:
    o.close()
print("Total: %d rows, Errors: %d rows" % (i, errors))
