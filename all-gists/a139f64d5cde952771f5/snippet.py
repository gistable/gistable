#!/usr/bin/env python
import socket
import sys

if len(sys.argv) != 3:
    print "Usage: %s video.mjpeg destfile.jpg" % sys.argv[0]
    sys.exit(1)

fh = open(sys.argv[1],'r')

print "Reading from file ..."

boundry = fh.readline().strip()
content_type = fh.readline().split(':')[1].strip()
length = int(fh.readline().split(':')[1].strip())

print "Pulling out image ..."

# i think we need to do this ...
fh.readline()

# read image contents
image = fh.read(length)

print "Writing out image file ..."

with open(sys.argv[2], 'w') as out_fh:
    out_fh.write(image)

print "Done."
