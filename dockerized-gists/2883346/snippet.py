#!/usr/bin/env python
# encoding: utf-8
"""
linkedin.py

Created by Edward Robinson on 2012-06-06.

You'll need to go find the password dump yourself.
Google combo_not.zip
"""
import sys
from hashlib import sha1

def main(plain, filename):
    print "looking for hash of < %s >" % plain
    off = 5
    pw_hash = sha1(plain).hexdigest()
    hashes = (pw_hash, '0' * off + pw_hash[off:])
    with open(filename, 'r') as f:
        dumped = set([x.strip().lower() for x in f])
    if hashes[0] in dumped:
        print "password %s in dump (not marked)." % plain
    elif hashes[1] in dumped:
        print "hash %s in dump and marked." % hashes[1]
    else:
        print "password %s not in dump." % plain
        
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python linkedin.py password <pass filename>"
    else:
        main(sys.argv[1], sys.argv[2])
