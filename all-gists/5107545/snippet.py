#!/usr/bin/python
#encoding utf-8
import sys, os
from itertools import takewhile 

def getFuncs(filename, funcDef = "def "):
    lines = open(filename,'r').readlines()
    funcDefIn = lambda line: True if line.strip().startswith(funcDef) else False
    funcs = map(lambda i: [lines[i]] + list(takewhile(lambda x: not funcDefIn(x),lines[i+1:])),filter(lambda i: funcDefIn(lines[i]),range(len(lines))))
    #                grabs lines until start of next func/end of file                        lines where functions start
    return funcs if len(funcs) > 0 else [lines]


def wordsInFunc(funclist, wordsToCount = ["if", "elif", "or", "and", "for", "while", "repeat"]):
    return map( lambda func: (func[0].split()[1].split("(")[0], sum(map(lambda line: sum( map(lambda x: line.split().count(x), wordsToCount)),func)) + 1) if len(func) > 0 else 0 ,funclist)
    #                       name of function                    sum of the Complexity of lines          sum of count of each word                   Base Complexity         

def summary(filename):
    print "%s:" % (filename)
    McCabeList = wordsInFunc(getFuncs(filename))
    for i,r in McCabeList:
        print "%s: %d" %( i,r)
    total = sum(map(lambda x: x[1],McCabeList))
    print "Total = %d" % (total)
    return total


def walkDir(dirname):
    s = 0
    for dirpath,dirnames,filenames in os.walk(dirname):
       s += sum( map( lambda x: summary(os.path.join(dirpath,x)) if x[-3:] == ".py"  else 0, filenames))
    print "Grand total %d" % (s)

dirname = sys.argv[1]
walkDir(dirname)
