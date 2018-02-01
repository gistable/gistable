#!/usr/bin/env python
import csv
try: import simplejson as json
except: import json
from optparse import OptionParser

def main():
  usage = "usage: csv2json: %prog [options] arg"
  parser = OptionParser()
  parser.add_option("-i","--input",dest="input",help="input csv file")
  parser.add_option("-o","--output", dest="output", help="output json file")

  (options, args) = parser.parse_args()
  
  input = open( options.input, 'rU' )
  output = open( options.output, 'w' )

  reader = csv.DictReader( input, fieldnames = input.readline().split(",") )
  output.write( json.dumps( [ row for row in reader ] ) )

if __name__ == "__main__":
  main()