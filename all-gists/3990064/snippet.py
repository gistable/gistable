#!/usr/bin/python
import re
import argparse
import locale

# Accept a sane looking network ID
parser = argparse.ArgumentParser(description='Syncie Log Parser')
parser.add_argument('-n', action="store", dest="network", type=int)
args = parser.parse_args()

# Format the network ID with commas
locale.setlocale(locale.LC_ALL, 'en_US')
euro_id = locale.format("%d", args.network, grouping=True)

# Do stuff
if args > 0:
    rg = re.compile('%s\W' % (euro_id), re.IGNORECASE | re.DOTALL)

    for line in open('/Users/blyttle/junk/syncielog.txt'):
        m = rg.search(line)
        if m:
            print line
