## This script will map a standard CSV file to a python list containing a dict for each row

import csv

reader = csv.reader(open('foobar.csv'), delimiter=',', quotechar='"')

fields = reader.next()  # field names are in the first line

results = []

for row in reader:
    results.append(dict(zip(fields, row)))

for result in results:
    print "%s: %s" % (result['Level'], result['Description'])