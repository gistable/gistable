#! /usr/bin/env python
"""
Remove duplicates rows from comma-separate value files.
Recommended for files saved in Windows CSV format.
Useful for situations where you will have duplicate data (e.g., sensor reads)

: param source : source csv file. Must end in .csv 

Result is destination csv file without duplicates.

Move to /usr/local/bin and chmod +x to use as command.
Can easily convert to function for real-time application.
"""

from sys import argv
import sys
import csv

# Check usage and provide help
if argv[1] in ('-h', '-help'):
	print "Usage: %s source-file.csv" % argv[0]
	sys.exit()
if len(argv) != 2: 
	usage = "Usage: %s source-file.csv" % argv[0]
	error = "You passed %d arguments." % len(argv)
	sys.exit("%s -- %s" % (usage, error))
if '.csv' not in argv[1]:
	usage = "Usage: %s source-file.csv" % argv[0]
	error = "You passed %r for source-file.csv" % argv[1]
	sys.exit("%s -- %s" % (usage, error))

# Create the output file as input with _deduped before .csv extension
source = argv[1]
destination = source.replace('.csv', '_deduped.csv')
data = open(source, 'r')
target = open(destination, 'w')
# Let the user know you are starting, in case you are de-dupping a huge file 
print "\nRemoving duplicates from %r" % source

# Initialize variables and counters
unique_lines = set()
source_lines = 0
duplicate_lines = 0

# Loop through data, write uniques to output file, skip duplicates.
for line in data:
	source_lines += 1
	# Strip out the junk for an easy set check, also saves memory
	line_to_check = line.strip('\r\n')	
	if line_to_check in unique_lines: # Skip if line is already in set
		duplicate_lines += 1
		continue 
	else: # Write if new and append stripped line to list of seen lines
		target.write(line)
		unique_lines.add(line_to_check)

# Be nice and close out the files
target.close()
data.close()

# Let the user know what you did
print "SUCCESS: Removed %d duplicate line(s) from file with %d line(s)." % \
 (duplicate_lines, source_lines)
print "Wrote output to %r\n" % destination