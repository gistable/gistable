#!/usr/bin/env python 

import subprocess
import sys

results = []

if not sys.stdin.isatty():
    input_stream = sys.stdin

for line in input_stream:
    if "ms\t" in line:
        if "<invalid" not in line:
            columns = line.split('\t')
            columns[0] = columns[0][:-2] # remove 'ms' from duration
            columns[2] = columns[2][:-1] # remove '\n' from end of line
            if float(columns[0]) >= 1.0:
                results.append(columns)
        
for result in results:
    for column in result:
        sys.stdout.write(column)
        sys.stdout.write("\t")
    sys.stdout.write('\n')
    
# use like `xcodebuild OTHER_SWIFT_FLAGS='-Xfrontend -debug-time-function-bodies' | <PATH_TO_THIS_SCRIPT>.py`