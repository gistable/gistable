#!/usr/bin/env python
"""Convert ranked ballots from the CSV format provided by CIVS
(http://www.cs.cornell.edu/andru/civs.html) to the BLT format
used by, e.g., OpenSTV (www.openstv.org/).

http://code.google.com/p/stv/wiki/BLTFileFormat

TODO: support the popular "text" format and equal rankings via the "=" delimiter.

%InsertOptionParserUsage%
"""

import os
import sys
import optparse
from optparse import make_option
import logging
import operator

__author__ = "Neal McBurnett <http://neal.mcburnett.org/>"
__copyright__ = "Copyright (c) 2009 Neal McBurnett"
__license__ = "GPL"
__version__ = "0.1.0"

usage = """Usage: rankconvert.py [options] file"""

option_list = (
    make_option("-n", "--numwin", dest="numwin", default=1,
                  help="number of winners", metavar="N"),

    make_option("-d", "--delimiter", dest="delimiter", default=',',
                  help="specify CSV delimiter", metavar="DELIMITER"),

    make_option("-v", "--verbose",
                  action="store_true", default=False,
                  help="verbose output" ),

    make_option("-D", "--debug",
                  action="store_true", default=False,
                  help="turn on debugging output"),
)

parser = optparse.OptionParser(prog="rankconvert", usage=usage, option_list=option_list)

# incorporate OptionParser usage documentation into our docstring
__doc__ = __doc__.replace("%InsertOptionParserUsage%\n", parser.format_help())

def rankconvert(parser):
    """convert file with ranked ballots to different format"""

    (options, args) = parser.parse_args()

    if options.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    logging.basicConfig(level=loglevel) # format='%(message)s'

    logging.debug("args = %s" % list(args))

    if len(args) != 1:
        logging.error("exactly one file should be specified")
        sys.exit(1)

    delimiter = options.delimiter

    reader = open(args[0])
    r = reader.next()
    choices = r.rstrip().split(delimiter)
    n = len(choices)

    print n,options.numwin

    for r in reader:
        weights = []
        for c in r.rstrip().split(delimiter):
            weights.append(int(c))
        last = max(weights)

        print "1",
        for (i,w) in sorted(enumerate(weights), key=operator.itemgetter(1)):
            if w == last:
                break
            # if there are more and weights are equal print = otherwise >
            print i+1,
        print "0"

    print "0"
    for choice in choices:
        print '"%s"' % choice
    print '"Ballot data converted by rankconvert"'

if __name__ == "__main__":
    rankconvert(parser)
