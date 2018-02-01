#!/usr/bin/env python

import sys
import re
import subprocess

RULES = [
    #'[javac] foo.java:6: cannot find symbol'
    [r'^ *\[javac\] ([^:]+:[^:]):(.*)$', '{0}: {1}'],
]

for rule in RULES:
    rule[0] = re.compile(rule[0])

def print_simplified_line(line, rules=RULES):
    for test, prod in rules:
        match = test.match(line)
        if not match: continue
        if prod:
            sys.stdout.write(prod.format(*match.groups()) + '\n')
            sys.stdout.flush()
        return

def run_simplified_ant(args):
    args = ['ant'] + args
    proc = subprocess.Popen(args, stdout = subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        line = proc.stdout.readline()
        if not line: break
        print_simplified_line(line)

    proc.wait()
    sys.exit(proc.returncode)

if __name__ == '__main__':
    run_simplified_ant(sys.argv[1:])
