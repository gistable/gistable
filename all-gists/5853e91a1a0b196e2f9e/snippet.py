#!/usr/bin/env python

# extract gzipped json data from packets with tshark
#
# e.g.: capture flight data from www.flightradar24.com
#  open www.flightradar24.com in a web browser
#  $ tshark -f "net 83.140.21.0/24" -i eth2 -w capture.cap
#  leave tshark running
#  $ ./extract.py

import zlib
import json

import shlex, subprocess

cmd = '''\
tshark \
-r capture.cap \
-Y 'http.content_type == "application/json" and http.content_encoding == "gzip"' \
-T fields -e data'''
args = shlex.split(cmd)

p = subprocess.Popen(args, stdout=subprocess.PIPE)
output, err = p.communicate()

for l in output.splitlines():
  if len(l) > 0:
    data = zlib.decompress(l.rstrip().decode("hex"),16+zlib.MAX_WBITS)
    data = json.loads(data)
    for key in data.keys():
      if type(data[key]) is list:
        print ','.join(map(str,data[key]))