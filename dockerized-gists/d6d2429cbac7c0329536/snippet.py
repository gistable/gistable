#!/usr/bin/env python
#coding=utf8
'''
usage:grep -nir SEARCH_STRING *.java | pickLine.py 3
search for SEARCH_STRING, and show 3 lines (containing current line) below that line
'''

import re
import sys
import os

gLineCount = 12

def isGrepOutput(s):
    return re.match('.*:.*', s) or re.match('.*:.*:.*', s)

def fileInfo(l):
    return re.match('(.*?):(.*?):.*', l).groups()

def pickLines(filename, startAtLine):
    with open(os.path.join(os.path.abspath('.'), filename)) as f:
        for i in range(int(startAtLine)-1):
            f.readline()
        for i in range(gLineCount):
            print f.readline(),

if __name__ == '__main__':
    l = sys.stdin.readline()
    while l and isGrepOutput(l):
        print '\033[93m'+re.match('(.*):.*', l).groups()[0]+'\033[0m'
        pickLines(*fileInfo(l))
        l = sys.stdin.readline()