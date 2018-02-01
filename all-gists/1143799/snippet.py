#!/usr/bin/env python
import socket
import sys 

if len(sys.argv) != 3:
    print "Usage: %s host:port destfile.jpg" % sys.argv[0]
    sys.exit(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host, port = sys.argv[1].split(':')
s.connect((host, int(port)))

fh = s.makefile()

# Read in HTTP headers:
line = fh.readline()
while line.strip() != '': 
    parts = line.split(':')
    if len(parts) > 1 and parts[0].lower() == 'content-type':
        # Extract boundary string from content-type
        content_type = parts[1].strip()
        boundary = content_type.split(';')[1].split('=')[1]
    line = fh.readline()

if not boundary:
    raise Exception("Can't find content-type")

# Seek ahead to the first chunk
while line.strip() != boundary:
    line = fh.readline()

# Read in chunk headers
while line.strip() != '': 
    parts = line.split(':')
    if len(parts) > 1 and parts[0].lower() == 'content-length':
        # Grab chunk length
        length = int(parts[1].strip())
    line = fh.readline()

image = fh.read(length)

with open(sys.argv[2], 'w') as out_fh:
    out_fh.write(image)

s.close()
