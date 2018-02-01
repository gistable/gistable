#!/usr/bin/env python
#!coding: utf-8

import sys, os, re, shutil
from optparse import OptionParser

parser = OptionParser(usage=
'''%prog [options] <target-dir>

Example:
  svn diff -r{2011-01-01}:HEAD --summarize ./ | %prog ../diff-files
  git diff --name-status HEAD~5 | %prog ../diff-files
  %prog -c 'git diff --name-status HEAD~5' ../diff-files
''')
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
              help="show parsed diff status")
parser.add_option("-c", "--command", dest="cmd",
              help="executable command line", metavar="COMMAND")
(options, args) = parser.parse_args()
if len(args) != 1:
    parser.print_help()
    exit(1)

target, = args

# clean target dir
if os.path.exists(target):
    for root, dirs, files in os.walk(target, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
else:
    os.makedirs(target)

if options.cmd:
    fd = os.popen(options.cmd, 'r')
else:
    fd = sys.stdin

# parse diff summary
overwrite = []
remove = []
for line in fd:
    line = line.strip()
    mo = re.match(r'^\s*([AMD])\s*(.*)$', line)
    if mo:
        if options.verbose:
            sys.stdout.write(line)
            sys.stdout.write("\n")
            sys.stdout.flush()
        if mo.group(1) in ['A', 'M']:
            overwrite.append(mo.group(2).strip(" \n"))
        elif mo.group(1) in ['D']:
            remove.append(mo.group(2).strip(" \n"))

if options.cmd:
    fd.close()

# copy added/modified files
for p in overwrite:
    s = p
    d = os.path.join(target, p)
    if os.path.isfile(s):
        if not os.path.exists(os.path.dirname(d)):
            os.makedirs(os.path.dirname(d))
        shutil.copy2(s, d)
    elif os.path.isdir(s):
        if not os.path.exists(d):
            os.makedirs(d)

# report if removed files found
if remove:
    fd = file(os.path.join(target, "__TO_BE_REMOVED__.txt"), "wt")
    for p in remove:
        fd.write("D %s\n" % p)
    fd.close()
