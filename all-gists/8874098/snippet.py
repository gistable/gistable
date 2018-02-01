#!/usr/bin/env python3
# coding=utf-8

import json
import sys

# only reads from stdin
j = json.loads(sys.stdin.read())

# reads a list of column names from the argument "col1,col2" etc
# if none is passed, uses the keys from the json in any order,
# therefore running multiple times will give different orders
try:
    cols = sys.argv[1].split(",")
except:
    cols = list(j[0].keys())

# calculates the size of the column. if a key doesn't exist on the input,
# an empty string will be set.
sizes = {k:len(k) for k in cols}
for item in j:
    for k in cols:
        try:
            sizes[k] = max(len(str(item[k])), sizes[k])
        except:
            try:
                sizes[k] = len(str(item[k]))
            except:
                item[k] = ""

de = " | "

# writes the header column
print("| " + de.join([c.ljust(sizes[c]) for c in cols]) + " |" )
# writes the separator column
print("| " + "-|-".join(["".ljust(sizes[c],"-") for c in cols]) + " |")

# writes the rows
for item in j:
    print("| " + de.join([str(item[k]).ljust(sizes[k]) for k in cols]) + " |")

