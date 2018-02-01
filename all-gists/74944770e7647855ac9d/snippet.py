#!/usr/bin/python


# USAGE:
# ./uuidconverter <file-in> <file-out>
#  file-in:  a file with 1 username per line
#  file-out: a file where name<tab>uuid are written to (appended)

from __future__ import print_function
import sys
import urllib2
import json
import re
from time import sleep

def convert(file_in, file_out):
  max_payload_size    = 100
  retriy_amount       = 3
  retry_request_delay = 1


  player_names = []
  regex        = re.compile("^[a-z0-9_]{1,16}$")
  with open(file_in) as f:
    for name in f.read().splitlines():
      low = name.lower()
      if not low == "steve" and regex.match(low) is not None:
        player_names.append(name)
      else:
        print("Invalid name: '%s'" % name, file=sys.stderr)

  print("now processing %s names..." % len(player_names))
  outfile = open(file_out, "a")

  for i in range((int(round(len(player_names) / float(max_payload_size)))) or 1):
    pos = i * max_payload_size
    players = player_names[pos:pos+max_payload_size]
    retrtries = 0
    request = urllib2.Request("https://api.mojang.com/profiles/minecraft",json.dumps(players),{"Content-Type": "application/json"})
    while retrtries < 3:
      retrtries += 1
      try:
        response = json.loads(urllib2.urlopen(request).read())
        for user in response:
          src = user["name"]
          dst = user["id"]
          print(src.ljust(20) + dst)
          outfile.write(src + "\t" + dst + "\n")
        break
      except urllib2.HTTPError as e:
        print(e, file=sys.stderr)
        print(str(players))
        print(request.get_data())
        print("(retrying in %s seconds..)" % retry_request_delay, file=sys.stderr)
        sleep(retry_request_delay)
  print("all done!")
  outfile.close()

if __name__ == "__main__":
  convert(sys.argv[1], sys.argv[2])