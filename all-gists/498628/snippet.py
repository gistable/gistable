#!/usr/bin/python3.1

# This is script that extracts the trees of two commits to temporary
# directories and then runs meld on both directories, so you can compare
# them using meld's nice recursive browsing interface.
#
# This is for an answer to this question:
#     http://stackoverflow.com/questions/2006032/view-differences-of-branches-with-meld

from subprocess import call, Popen, PIPE, check_call
import sys
from tempfile import mkdtemp
from shutil import rmtree

if len(sys.argv) != 3:
    print("Usage: {} <refA> <refB>".format(sys.argv[0]),file=sys.stderr)
    sys.exit(1)

ref1, ref2 = sys.argv[1:]

def check_ref(ref):
    print("Checking "+ref+":")
    return 0 == call(["git","rev-parse","--verify",ref])

ref1_ok = check_ref(ref1)
ref2_ok = check_ref(ref2)

if not (ref1_ok and ref2_ok):
    # git rev-parse will have output an error, so just exit
    sys.exit(1)

dir1 = mkdtemp()
dir2 = mkdtemp()

# From http://stackoverflow.com/questions/35817/whats-the-best-way-to-escape-os-system-calls-in-python
def shellquote(s):
    return "'" + s.replace("'", "'\\''") + "'"

def extract_tree_to(tree,output_directory):
    check_call("git archive {} | tar -C {} -x".format(shellquote(tree),
                                                      shellquote(output_directory)),
               shell=True)

try:
    extract_tree_to(ref1,dir1)
    extract_tree_to(ref2,dir2)
    call(["meld",dir1,dir2])
finally:
    rmtree(dir1)
    rmtree(dir2)
