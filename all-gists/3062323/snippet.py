#!/usr/bin/env python
import sys

Dict = []
with open('aclImdb/imdb.vocab','r') as f:
    for line in f:
        Dict.append(line.strip())

with open('audit.log','r') as f:
    f.readline()
    line = f.readline()
    parts = line.split()
    for part in parts:
        if part[0]=='C': continue
        bits = part.split(":")
        wordidx = int(bits[0].split("^")[1])
        if float(bits[3]) > 0: sent = '+'
        elif float(bits[3]) < 0: sent = '-'
        else: sent = '?'
        if wordidx < 1000:
            print "%20s: %s %0.4f" % (Dict[wordidx], sent, abs(float(bits[3])))
