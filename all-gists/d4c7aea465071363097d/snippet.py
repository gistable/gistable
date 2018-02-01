# Read CSV of rent stabilized properties and grab BBL from NYC's GeoClient API
# takes an input CSV file name and output CSV file name as argv
# first two columns of input csv must be address number and address name
# hardcoded for manhattan only, will update in the future 
# run script by doing: python geo-client-api-test.py input.csv output.csv

from sys import argv
from nyc_geoclient import Geoclient
import csv
import json

script, infile, outfile = argv

g = Geoclient('9cd0a15f', '54dc84bcaca9ff4877da771750033275')

#test = g.address('140-154', 'West 72nd Street', 'Manhattan')
#print json.dumps(test, sort_keys=True)

print "opening file: %s" % infile
with open(infile, 'r') as i:

    reader = csv.reader(i)   

    print "opening file: %s" % outfile
    with open(outfile, 'w') as o:

        writer = csv.writer(o, lineterminator='\n')        
        all = []
        row = next(reader, None)
        row.append('bbl')
        all.append(row)
        
        try:
            for row in reader:                

                street_num = row[0]
                street_name = row[1]
                #print street_num, street_name
                
                row_gc = g.address(street_num, street_name, 'Manhattan')                
                row_bbl = row_gc.get('bbl', '0' )
                
                print "The BBL for %s %s is %s" % (street_num, street_name, row_bbl)                
                row.append(row_bbl)
                all.append(row)

            writer.writerows(all)

        except csv.Error as e:            
            sys.exit('file %s, line %d: %s' % (infile, reader.line_num, e))
