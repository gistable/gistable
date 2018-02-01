#!/usr/bin/env python

from os.path import isfile
from sys import argv
from time import sleep

import commands
import select

suffix = argv[1] if len(argv) > 1 else ""
fn_list = []
fh_list = []

last_file = None

while True:
    file_names = commands.getoutput('ls -d *' + suffix).split('\n')

    for file_name in file_names:
        if isfile(file_name) and file_name not in fn_list:
            f = open(file_name, 'r')
            if f:
                f.seek(0, 2)
                fh_list.append(f)
                fn_list.append(file_name)
            else:
                print "could not open '{fn}'\n".format(fn=file_name)
        else:
            next

    ready = select.select(fh_list, [], [])
    for fh in ready:
        current_pos = fh.tell()
        line = fh.readline()
        if line:
            if fh.name != last_file:
                print "\n\x1b[33m[{n}]      \x1b[0m".format(n=fh.name)
                last_file = fh.name
            print line.rstrip()

    sleep(0.1)
