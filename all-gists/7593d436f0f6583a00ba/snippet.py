import commands
import subprocess
import os
import sys

DO_NOT_DELETE_BRANCHES = ['main',]
SRC_DIRECTORY = '/Users/Saurabh/f6/trunk/f6/'
GIT_BINARY_LOCATION = '/usr/bin/git'
pr = subprocess.Popen(
  GIT_BINARY_LOCATION + " branch",
  cwd = os.path.dirname(SRC_DIRECTORY),
  shell = True,
  stdout = subprocess.PIPE,
  stderr = subprocess.PIPE
)

(branches, error) = pr.communicate()

if error:
  print "ERROR: %s" % repr(error)
else:
  branches = branches.split('\n')
  for branch in branches:
    if not branch:
      continue
    should_branch_be_deleted = True
    for do_not_delete_branch in DO_NOT_DELETE_BRANCHES:
      if do_not_delete_branch in branch.strip():
        should_branch_be_deleted = False
    #delete the branch
    if not should_branch_be_deleted:
      continue
    print "Deleting %s" % branch.strip()
    pr = subprocess.Popen(
      GIT_BINARY_LOCATION + " branch -D %s" % branch.strip(),
      cwd = os.path.dirname(SRC_DIRECTORY),
      shell = True,
      stdout = subprocess.PIPE,
      stderr = subprocess.PIPE
    )
    print "Deleted %s" % branch.strip()
