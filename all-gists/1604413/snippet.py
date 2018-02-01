#!/usr/bin/python
import os
import sys

def listdir(d):
    if not os.path.isdir(d):
        print d
    else:
        for item in os.listdir(d):
            listdir((d + '/' + item) if d != '/' else '/' + item)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: listall DIR'
    else:
        listdir(sys.argv[1])