#!/usr/bin/env python

import os
import sys
import urllib2
import json
import hashlib
import zlib
from optparse import OptionParser

def main():
  parser = OptionParser(usage='catalog')
  options, args = parser.parse_args()
  catfile = open(args[0], 'r')
  parsed_cat = json.loads(catfile.read())
  image_list = parsed_cat['images']
  for image in image_list:
#    print image['name']
    filename = image['url']
    filename = filename[filename.rfind("/")+1:]
    try:
      file = open(filename, 'r')
      m = hashlib.md5()
      m.update(file.read())
      hash = m.hexdigest()
      crc = str(zlib.crc32(hash)& 0xffffffffL)
#      print crc.rjust(10,"0")
      image['name'] = crc.rjust(10,"0")
    except (IOError):
      print "file not found: "+filename

  print json.dumps(parsed_cat, indent=2)

if __name__ == "__main__":
    main()