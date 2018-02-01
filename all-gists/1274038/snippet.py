#!/usr/bin/env python3
"""
Tests http mirrors of cygwin
"""
import random
import time
from urllib.request import  urlopen
import sys

__author__ = 'Dmitry Sidorenko'

mirrors_url = "http://cygwin.com/mirrors.lst"
test_file = "/x86_64/setup.ini"

mirrors = [
  #    {"host": "",
  #     "time": 1
  #  }
]
print("Downloading mirrors list...", end='')
sys.stdout.flush()
u = urlopen(mirrors_url)
for line in u:
  strline = str(line)[2:-3]
  host = strline.split(";")
  # Only test http
  if host[0].startswith("http://"):
    mirrors.append({"host": host, "time": 9999})
print("done, %d entries" % len(mirrors))
random.shuffle(mirrors)

block_sz = 8096
max_hosts_to_try = 100
testn = 1
for hostentry in mirrors:
  host = hostentry["host"]
  print("testing mirror %s ..." % host[1], end='')
  sys.stdout.flush()
  start_time = time.time()
  try:
    test = urlopen(host[0] + test_file, timeout=5)
    test.read(block_sz)
    time_spent = time.time() - start_time
    hostentry["time"] = time_spent
    print("%s sec" % time_spent)
  except IOError:
    hostentry["time"] = 9999
    print("timeout")
  testn += 1
  if testn > max_hosts_to_try:
    break

mirrors = sorted(mirrors, key=lambda entry: entry["time"])

print("\nTop 5 mirrors\n")
sys.stdout.flush()

for i in range(5):
  mirror = mirrors[i]
  host_info = mirror["host"]
  if mirror["time"] < 9999:
    print("%.3f, %14s, %10s, %s" % (mirror["time"], host_info[2], host_info[3], host_info[0]), file=sys.stderr)

