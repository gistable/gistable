#!/usr/bin/env python
"is_hard.py - tell if two files are hard links to the same thing"

import os, sys, stat

def is_hard_link(filename, other):
    s1 = os.stat(filename)
    s2 = os.stat(other)
    return (s1[stat.ST_INO], s1[stat.ST_DEV]) == \
        (s2[stat.ST_INO], s2[stat.ST_DEV])

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "Two arguments required"
    else:
        if is_hard_link(sys.argv[1], sys.argv[2]):
            print "Hard link confirmed"
        else:
            print "Those are different files, no hard link"
