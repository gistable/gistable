#!/usr/bin/python

import sys;
import re;
import slate;
import pickle;
import nltk;
import glob;
import os;

def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: %s search-term' % sys.argv[0])

targets = glob.glob('./*.pdf')

for target in targets:
    print("searching in: " + target)
    with open(target) as f:
        doc = slate.PDF(f)

    for i in range (0,len(doc)):
        if sys.argv[1].lower() in doc[i].lower():
            print("FOUND! in page " + str(i+1))

if __name__ == "__main__":
    main()