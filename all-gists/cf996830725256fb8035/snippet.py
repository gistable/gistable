#!/usr/bin/env python
# Copyright 2015 Ryan Castellucci
# License: http://opensource.org/licenses/BSD-3-Clause

import sys
import time
import base64
import subprocess

from struct import pack, unpack

def b32e(n):
    return base64.b32encode(pack('>Q', n - 1)[3:]).lower()

def b32d(s):
    return unpack('>Q', "\0\0\0"+base64.b32decode(s, True))[0] + 1

# timestamp
def ts():
    return time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())

# returns the largest value x for n, where n % 2**x == 0
def lp2(n):
    x = 0
    if n < 1: return -1
    while ((n >> x) & 1 == 0): x += 1
    return x

# figure out which backups are expired
def toremove(l, n):       
    p = lp2(n)
    return [i for i in l if lp2(i) == p]

basedir = sys.argv[1]

# TODO error handling
# get a list of existing snapshots
snapshots = {}
proc = subprocess.Popen(["btrfs", "subvolume", "list", basedir],
                        stdout=subprocess.PIPE)
for line in proc.stdout:
    snapshot = line.split(' ')[8].strip()
    if snapshot.startswith('.snap/hanoi-'):
        (path, timestamp, ident) = snapshot.split('-')
        snapshots[b32d(ident)] = basedir + "/" + snapshot

# list of numeric snapshot ids
ids = snapshots.keys()

# figure out what the next backup id is and what, if anything, should be removed
rem = []
if len(ids) == 0:
    n = 1
else:
    n = max(ids) + 1
    rem = toremove(ids, n)

# TODO explicit error handling
# create new snapshot - if this fails, program will abort
subprocess.check_call(["btrfs", "subvolume", "snapshot", "-r", basedir,
                      "%s/.snap/hanoi-%s-%s" % (basedir, ts(), b32e(n))])

# delete old snapshot(s), if any - normally should be at most one
for i in rem:
    subprocess.check_call(["btrfs", "subvolume", "delete", snapshots[i]])