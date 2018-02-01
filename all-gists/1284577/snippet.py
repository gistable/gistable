#!/usr/bin/env python

import sys
import yaml
import pprint

filename = sys.argv[1]

y = yaml.safe_load(open(filename, 'r'))

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(y)
