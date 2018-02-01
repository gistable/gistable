#!/bin/env python

import yaml
import sys
import json
import argparse
from subprocess import Popen, PIPE
import argparse
import os

exists=os.path.isfile

def json_serial(obj):
    # all obj's dumped to str
    return str(obj)

# look for jq arguments, vs file arguments
offset=1
for arg in sys.argv[1:]:
    if arg and arg[0] == '-' and not exists(arg):
        ++offset
    else:
        break

# construct arguments so that it looks like jq
files=[]
frm=[0]
index=offset
for arg in sys.argv[offset:]:
    if exists(arg):
       files.append(arg)
       frm.insert(0,index)
    index+=1

for index in frm:
    sys.argv.pop(index)


if sys.argv:
    # jq args are present
    args=["jq"]+sys.argv
    pipe = Popen(args, stdin=PIPE).stdin
else:
    # no jq args... just dump to stdout
    pipe = sys.stdout

if files:
    for fin in files:
        json.dump(yaml.load(open(fin)),pipe,default=json_serial)
else:
        json.dump(yaml.load(sys.stdin),pipe,default=json_serial)
