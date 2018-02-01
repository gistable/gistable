#!/usr/bin/env python

import sys
import exifread
import time
from os import path, utime

k = 'EXIF DateTimeOriginal'

for fn in sys.argv[1:]:

  # Open image file for reading (binary mode)
  f = open(fn, 'rb')

  # Return Exif tags
  tags = exifread.process_file(f)

  if not k in tags:
    continue

  ''' exif date '''
  exif_time = tags[k].__str__()
  ''' creation date '''
  o = time.mktime(time.strptime(exif_time, '%Y:%m:%d %H:%M:%S'))

  m = path.getmtime(fn)

  if not m == o:
    print "Change time of %s!" % fn
    utime(fn, (o, o))
