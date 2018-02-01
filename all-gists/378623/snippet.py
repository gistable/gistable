#!/bin/env python
"""mergelog

This is a custom merge driver for git. It should be called from git
with a stanza in .git.config like this:

    [merge "mergelog"]
        name = A custom merge driver for my log.txt file.
        driver = ~/scripts/mergelog %O %A %B %L
        recursive = binary

To make git use the custom merge driver you also need to put this in
.git/info/attributes:

   log.txt merge=mergelog

This tells git to use the 'mergelog' merge driver to merge files called log.txt.

"""
import sys, difflib

class DiffError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def get_difference(one,two):
    """Return those lines of text from the beginning of list `two` that
    are not present at the beginning of list `one`.

    one     The base text, a list of strings.
    two     The modified text, a list of strings.

    `one` and `two` should be the same except that `two` may begin with
    some lines that are not present in `one`. If the diff of `one` and
    `two` produces any other results (if in producing `two`some text was
    subtracted from `one`, if text was added to `one` elsewhere than at
    the top of the file, or if more than one hunk of text was added to
    `one`) an assertion will be raised.
    """
    d = difflib.Differ()
    diff = d.compare(one,two)
    mode = 0
    added_lines = []
    for line in diff:
        if mode == 0:
            if line.startswith('+ '):
                added_lines.append(line[2:])
            else:
                if line.startswith('  '):
                    mode = 1
                else:
                    raise DiffError(diff)
        elif mode == 1:
            if not line.startswith('  '):
                raise DiffError(diff)
    return added_lines

# The arguments from git are the names of temporary files that
# hold the contents of the different versions of the log.txt
# file.

# The version of the file from the common ancestor of the two branches.
# This constitutes the 'base' version of the file.
ancestor = open(sys.argv[1],'r').readlines()

# The version of the file at the HEAD of the current branch.
# The result of the merge should be left in this file by overwriting it.
current = open(sys.argv[2],'r').readlines()

# The version of the file at the HEAD of the other branch.
other = open(sys.argv[3],'r').readlines()

# The merge algorithm is as follows:
# Append any text that was added to the beginning of the file in the
# other branch to the beginning of the current branch's copy of the file.
# If the other branch contains changes other than adding text at the
# beginning of the file then fail.
try:
    ancestor_to_other = get_difference(ancestor,other)
except DiffError, d:
    print ''.join(difflib.unified_diff(ancestor,other))
    sys.exit(1)

print "The following text will be appended to the top of the file:"
print ''.join(ancestor_to_other)
f = open(sys.argv[2],'w')
f.writelines(ancestor_to_other)
f.writelines(current)
f.close()

# Exit with zero status if the merge went cleanly, non-zero otherwise.
sys.exit(0)