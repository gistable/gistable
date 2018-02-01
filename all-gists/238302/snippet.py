# pre-commit.py:
#
# Performs the following:
#  - Makes sure the author has entered a log message.
#  - Makes sure the author is only creating a tag, or if deleting a tag, author is a specific user
#  - Makes sure the author is not committing to a particular set of paths in the repository
#
# Script based on http://svn.collab.net/repos/svn/trunk/tools/hook-scripts/log-police.py
#
# usage: pre-commit.py -t TXN_NAME REPOS
# e.g. in pre-commit.cmd (under Windows)
#
#   PATH=C:\Python26;C:\Python26\Scripts
#   python.exe {common_hooks_dir}\pre_commit.py -t %2 %1

import os
import sys
import getopt
try:
  my_getopt = getopt.gnu_getopt
except AttributeError:
  my_getopt = getopt.getopt

import re

import svn
import svn.fs
import svn.repos
import svn.core

# Check Tags functionality
def check_for_tags(txn):
  txn_root = svn.fs.svn_fs_txn_root(txn)
  changed_paths = svn.fs.paths_changed(txn_root)
  for path, change in changed_paths.iteritems():
    if is_path_within_a_tag(path): # else go to next path
      if is_path_a_tag(path):
        if (change.change_kind == svn.fs.path_change_delete):
          if not is_txn_author_allowed_to_delete(txn):
            sys.stderr.write("\nOnly an administrator can delete a tag.\n\nContact your Subversion Administrator for details.")
            return False
        elif (change.change_kind != svn.fs.path_change_add):
          sys.stderr.write("\nUnable to modify %s.\n\nIt is within a tag and tags are read-only.\n\nContact your Subversion Administrator for details." % path)
          return False
        # else user is adding a tag, so accept this change
      else:
        sys.stderr.write("\nUnable to modify %s.\n\nIt is within a tag and tags are read-only.\n\nContact your Subversion Administrator for details." % path)
        return False
  return True

def is_path_within_a_tag(path):
  return re.search('(?i)\/tags\/', path)

def is_path_a_tag(path):
  return re.search('(?i)\/tags\/[^\/]+\/?$', path)

def is_txn_author_allowed_to_delete(txn):
  author = get_txn_property(txn, 'svn:author')
  return (author == 'admin')

# Check log message functionality
def check_log_message(txn):
  log_message = get_txn_property(txn, "svn:log")
  if log_message is None or log_message.strip() == "":
    sys.stderr.write("\nYou have engaged in the obscene act of attempting to commit without a log message.\n\nPlease make another attempt, preferably including the Jira issue number in the log message.")
    return False
  else:
    return True

# Check disallowed commit paths functionality
def check_disallowed_commit_paths(txn):
  txn_root = svn.fs.svn_fs_txn_root(txn)
  changed_paths = svn.fs.paths_changed(txn_root)
  for path, change in changed_paths.iteritems():
    if is_commit_disallowed(path):
	  sys.stderr.write("\nYou are not currently allowed to commit to the path %s.\n\nContact your Subversion Administrator for details." % path)
	  return False
  return True

def is_commit_disallowed(path):
  disallowed_commit_paths = ['/branches/9.7', '/branches/9.8']
  for d in disallowed_commit_paths:
    if path.find(d) != -1:
	  return True
  return False

def get_txn_property(txn, prop_name):
  return svn.fs.svn_fs_txn_prop(txn, prop_name)

def usage_and_exit(error_msg=None):
  import os.path
  stream = error_msg and sys.stderr or sys.stdout
  if error_msg:
    stream.write("ERROR: %s\n\n" % error_msg)
  stream.write("USAGE: %s -t TXN_NAME REPOS\n"
               % (os.path.basename(sys.argv[0])))
  sys.exit(error_msg and 1 or 0)

def main(ignored_pool, argv):
  repos_path = None
  txn_name = None

  try:
    opts, args = my_getopt(argv[1:], 't:h?', ["help"])
  except:
    usage_and_exit("problem processing arguments / options.")
  for opt, value in opts:
    if opt == '--help' or opt == '-h' or opt == '-?':
      usage_and_exit()
    elif opt == '-t':
      txn_name = value
    else:
      usage_and_exit("unknown option '%s'." % opt)

  if txn_name is None:
    usage_and_exit("must provide -t argument")
  if len(args) != 1:
    usage_and_exit("only one argument allowed (the repository).")

  repos_path = svn.core.svn_path_canonicalize(args[0])

  fs = svn.repos.svn_repos_fs(svn.repos.svn_repos_open(repos_path))
  txn = svn.fs.svn_fs_open_txn(fs, txn_name)

  if check_log_message(txn) and check_for_tags(txn) and check_disallowed_commit_paths(txn):
    sys.exit(0)
  else:
    sys.exit(1)

if __name__ == '__main__':
  sys.exit(svn.core.run_app(main, sys.argv))
