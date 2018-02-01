# Copyright 2015 Paul Brewer Economic and Financial Technology Consulting LLC                                                                                                                            
# Released under the MIT Public License                                                                                                                                                                  
# LICENSE: http://opensource.org/licenses/MIT                                                                                                                                                            
# Purpose:  rationally removes inner commas and inner quotes from csv file fields                                                                                                                        
# Useful for Google BigQuery as of 2015-03 does not support quoted commas in CSV fields                                                                                                                  
# python ./unfubarcsv.py INFILE.csv OUTFILE.csv                                                                                                                                                          
import csv
import sys
import re
infile = open(sys.argv[1],'r')
outfile = open(sys.argv[2],'w')
csvin = csv.reader(infile)
csvout = csv.writer(outfile, quoting=csv.QUOTE_ALL)
for rowin in csvin:
    rowout = []
    for origfield in rowin:
        field = origfield[1:-1] if origfield[0:1]=='"' else origfield
        field = field.replace(r'"',r' ')
        field = field.replace(r"'",r" ")
        while field != re.sub(r'(\d+),(\d+)', r'\1\2', field):
            field = re.sub(r'(\d+),(\d+)', r'\1\2', field)
        field = field.replace(r',',r' ')
        rowout.append(field)
    csvout.writerow(rowout)
