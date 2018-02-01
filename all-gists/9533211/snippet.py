#!/usr/bin/python
import csv
import sys
import argparse
import io

csv.field_size_limit(sys.maxsize)

parser = argparse.ArgumentParser(description='Clean csv of in-line newlines')
parser.add_argument('infile',help='Path to input CSV file');
parser.add_argument('outfile',help='Path to output CSV file');
args = parser.parse_args();

inf =  file(args.infile,'r')
outf = file(args.outfile,'w')

try:
	reader = csv.reader(inf)
	writer = csv.writer(outf)
	for row in reader:
		newrow = [col.replace('\r\n', '##').replace('\n','##') for col in row]
		writer.writerow(newrow)

finally:
	inf.close()
	outf.close()