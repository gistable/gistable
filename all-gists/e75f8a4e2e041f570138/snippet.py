#!/usr/bin/env python

import sys
import os
from subprocess import check_call
from lxml import etree

if len(sys.argv) != 2:
    print >> sys.stderr, "Usage: %s [EMX-FILE]" % (sys.argv[0])
    sys.exit(1)

data = etree.parse(sys.argv[1])

for tu in data.xpath("//TRACKURL"):    
    check_call(['wget','-c',tu.text])