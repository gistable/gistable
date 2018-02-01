#!/usr/bin/env python

'''
Makes template filenames for interpolating Himawari-8 data.
Assumes filenames like "2015-11-28T023500.png".
I do this: python betwixt.py day-color | parallel --colsep ' ' convert -average {1} {2} {3}
'''

import os
import sys

def addfive(n):
  tenmin = int(n[13:15])
  later = tenmin + 5
  return '%s%02d%s' % (n[:13], later, n[15:])

def display(dirpath, a, b, c):
  print('%s %s %s' % 
    tuple(os.path.join(dirpath, x) for x in (a, b, c)))

dirpath = sys.argv[1]

ls = [p for p in os.listdir(dirpath) if not p.startswith('.')]
ls.sort()

for idx in range(len(ls)):
  if idx < len(ls)-1:
    display(dirpath,
      ls[idx],
      ls[idx+1],
      addfive(ls[idx])
    )
  
  else:
    display(dirpath,
      ls[idx],
      ls[0],
      addfive(ls[idx])
    )