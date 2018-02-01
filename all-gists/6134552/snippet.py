#!/usr/bin/env python
 
# Copyright 2013 Evernote Corporation. All rights reserved.
 
import base64
import sys
 
# Copy the base64 string from the ENEX file and put it into a file
 
# Pipe base64-encoded data to STDIN
data = sys.stdin.read()
 
# Decode data
try:
    imgraw = base64.b64decode(data)
except TypeError, te:
    print 'TypeError: ', te
    raise SystemExit
 
# Write it to the file passed as a param
with file(sys.argv[1], 'wb') as outfile:
    outfile.write(imgraw)
 
## Usage:
## (Change myfile.ext to the desired filename and correct extension)
 
# cat base64File | python b64dec.py myfile.ext
 
## or, if you base64 data is in the pasteboard on a Mac:
 
# pbpaste | python b64dec.py myfile.ext