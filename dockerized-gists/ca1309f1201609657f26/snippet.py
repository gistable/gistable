#!/usr/bin/python

from __future__ import print_function
import prettytable
import csv
import sys

def main(argv):
  if len(sys.argv) != 3:
    print('Usage: python csv2table.py [input file] [output]\n')
    exit(1)

  inputfile = sys.argv[1]
  outputfile = sys.argv[2]

  table = None
  with open(inputfile, 'rb') as csvfile:
    content = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in content:
      if table is None:
        table = prettytable.PrettyTable(row)
      else:
        table.add_row(row)

  output = open(outputfile, 'w')
  print(table, file=output)

  print('Done.\n')

if __name__ == "__main__":
  main(sys.argv[1:])