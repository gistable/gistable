#!/usr/bin/python
# coding=utf-8

# Python version of Zach Holman's "spark"
# https://github.com/holman/spark
# by Stefan van der Walt <stefan@sun.ac.za>

"""
USAGE:

  sparks.py [comma,separated,value,list] or [vals separated by spaces]

EXAMPLES:
  spark 1,5,22,13,53
  ▁▁▃▂▇
  spark 0 30 55 80 33 150 
  ▁▂▃▅▂▇
  spark 0.1 0.2 0.9 -0.5
  ▄▅█▁
"""

import sys
import numpy as np

if len(sys.argv) < 2:
    print __doc__
    sys.exit(-1)

sparks = np.fromstring('▁▂▃▄▅▆▇█', dtype='S3')
values = np.array([float(v) for v in ' '.join(sys.argv[1:]).replace(',', ' ').split()])
if np.unique(values).size != 1:
    values -= values.min()

m = values.max() or 1
values /= m

print sparks[np.round(values * (sparks.size - 1)).astype(int)].tostring()
