#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json

tobj = list()
statusfile = 'serverstatus.dat'
statusfile_output = 'serverstatus.json'
currentobj = dict()
reg = re.compile(r'^\s*$')

with open(statusfile, 'r') as f:
    for line in f.read().split('\n'):
        if line.startswith('#'):
            continue
        if reg.match(line):
            continue
        if '{' in line:
            currentobj = dict()
            currentobj['serverstatus-name'] = line[:-2]
            continue
        elif '}' in line:
            if currentobj:
                tobj.append(currentobj)
                currentobj = None
            continue
        else:
            if currentobj:
                key, value = [x.strip() for x in line.split('=',1)]
                currentobj[key] = value

with open(statusfile_output, 'w') as w:
    json.dump(tobj, w)