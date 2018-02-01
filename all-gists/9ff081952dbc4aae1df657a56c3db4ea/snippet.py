#!/usr/bin/env python
#-*- coding: utf-8 -*-
# Supporting Python 3 

import sys, os, re

try:    bibtexdb = open(sys.argv[1]).read()
except: print("Error: specify the file to be processed!")

if not os.path.isfile('journalList.txt'):
    import urllib
    urllib.urlretrieve("https://raw.githubusercontent.com/JabRef/jabref/master/src/main/resources/journals/journalList.txt", 
            filename="journalList.txt")
rulesfile = open('journalList.txt')

for rule in rulesfile.readlines()[::-1]:           ## reversed alphabetical order matches extended journal names first
    pattern1, pattern2 = rule.strip().split(" = ")
    if pattern1 != pattern1.upper() and (' ' in pattern1):        ## avoid mere abbreviations
        #bibtexdb = bibtexdb.replace(pattern1.strip(), pattern2.strip())    ## problem - this is case sensitive
        repl = re.compile(re.escape(pattern1), re.IGNORECASE)               ## this is more robust, although ca. 10x slower
        (bibtexdb, num_subs) = repl.subn(pattern2, bibtexdb)
        if num_subs > 0:
            print "Replacing '%s' FOR '%s'" % (pattern1, pattern2)

with open('abbreviated.bib', 'w') as outfile:
    outfile.write(bibtexdb)
    print "Bibtex database with abbreviated files saved into 'abbreviated.bib'"
