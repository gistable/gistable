#!/usr/bin/env python
"""
Shows git branches sorted by last commit date, noting when branch has been
merged:

    $ git blast
    * master 33 minutes ago
      david 4 days ago [M]
      unholy-david-payments 4 days ago
      handsontable-2 5 days ago
      payments 5 days ago [M]
      ask-inst-type 7 days ago
      legacy 2 weeks ago
      archive 2 weeks ago
      upload 3 weeks ago
      david-old 4 months ago
      dbscan 5 months ago
      matrix-fun 5 months ago
"""

import subprocess as sp

def xcall(cmd):
    return sp.check_output(cmd.split()).decode("utf-8")

C_GREEN = '\033[0;32m'
C_BLUE = '\033[0;34m'
C_RESET = '\033[0;0m'

cur_branch = xcall("git rev-parse --abbrev-ref HEAD").strip()
merged_branches = set([
    x.split()[-1] for x
    in xcall("git branch --merged").splitlines()
])

by_date = xcall(
    "git for-each-ref --sort=-committerdate refs/heads/ "
    "--format=%(refname:short)%09%(committerdate:relative)"
)
for line in by_date.splitlines():
    branch, _, date = line.partition("\t")
    output = ""
    if branch == cur_branch:
        output += "* %s%s" %(C_GREEN, branch)
    else:
        output += "  %s" %(branch, )
    output += " %s%s%s" %(C_BLUE, date, C_RESET)
    if branch in merged_branches and branch != cur_branch:
        output += " [%sM%s]" %(C_GREEN, C_RESET)
    print(output)