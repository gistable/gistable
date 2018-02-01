"""
1Password is good at a lot of things. Importing CSV is not one of them (as of 5.5.BETA-29).
Converts a Meldium CSV to something 1Password will import correctly.

To export: http://support.meldium.com/knowledgebase/articles/656755-export-meldium-data-to-a-spreadsheet
"""

import csv
import sys

def main():
    if len(sys.argv) < 3:
        print 'usage: meldium_to_1password.py input_filename output_filename'
        return

    infile = open(sys.argv[1], 'r')
    outfile = open(sys.argv[2], 'w')
    
    convert(infile, outfile)
    
    infile.close()
    outfile.close()

def convert(infile, outfile):
    reader = csv.DictReader(infile)
    writer = csv.writer(outfile)

    convert = 0
    for row in reader:
        keys = ["DisplayName","Url","UserName","Password","Notes"]
        writer.writerow([row[x] for x in keys])
        convert += 1

    print 'converted %d entries' % convert

if __name__ == '__main__':
    main()

