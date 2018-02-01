#!/usr/bin/env python2

# git-branch-io -- show incoming and outgoing commits
#
# Place this file somewhere in your PATH.
#
# Usage: git branch-io [branch]
#
# If branch is not given the current branch will be used.  The script
# prints out how many commits should go in either direction to bring
# branches in sync. For example:
#
# $ git branch-io master
# Comparing with branch master
#   master  23> <1   feature1
#   master   0> <12  feature2
#   master   0> <0   feature3
#
# Here 23 commits from master are missing in feature1 and one commit
# from feature1 is missing in master.

import sys
import subprocess
from optparse import OptionParser

# Copied from SO http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

_BRANCHES = None


def error_exit(msg, status_code=1):
    sys.stderr.write('%s\n' % msg)
    sys.exit(status_code)


def get_branches():
    global _BRANCHES
    if _BRANCHES is None:
        p = subprocess.Popen(['git', 'branch'], stdout=subprocess.PIPE)
        p.wait()
        _BRANCHES = []
        for line in p.stdout.readlines():
            is_current = '*' in line
            line = line.replace('*', '')
            _BRANCHES.append((is_current, line.strip()))
    return _BRANCHES

def get_active_branch():
    for is_current, branch in get_branches():
        if is_current:
            return branch
    error_exit('Unable to find active branch.')

def assert_branch(name):
    for _, branch in get_branches():
        if branch == name:
            return
    error_exit('No such branch %r.' % name)


def get_branch_info(ref, branch):
    ret = {'in': 0, 'out': 0}
    p = subprocess.Popen(['git', 'log', '--pretty=oneline',
                          '%s..%s' % (ref, branch)], stdout=subprocess.PIPE)
    p.wait()
    ret['out'] = len(p.stdout.readlines())
    p = subprocess.Popen(['git', 'log', '--pretty=oneline',
                          '%s..%s' % (branch, ref)], stdout=subprocess.PIPE)
    p.wait()
    ret['in'] = len(p.stdout.readlines())
    return ret


def set_colors(data, key, ckey):
    if data[key] == 0:
        data[ckey] = OKGREEN
    elif data[key] > 10:
        data[ckey] = FAIL
    elif data[key] > 2:
        data[ckey] = WARNING
    else:
        data[ckey] = OKBLUE


def main(ref, opts):
    assert_branch(ref)
    print 'Comparing with branch %s' % ref
    unsynced = []
    for _, branch in get_branches():
        if branch == ref:
            continue
        data = {'ref': ref, 'branch': branch,
                'col2': '', 'colend': ENDC, 'col1': ''}
        data.update(get_branch_info(ref, branch))
        if data['out'] == 0 and data['in'] == 0 and not opts.show_synced:
            continue
        if data['out'] != 0 or data['in'] != 0:
            unsynced.append(branch)
        if opts.colored:
            set_colors(data, 'out', 'col2')
            set_colors(data, 'in', 'col1')
        print ('  %(col1)s%(ref)s %(in)3d>%(colend)s '
               '%(col2)s<%(out)-3d %(branch)s%(colend)s' % data)
    if not unsynced and not opts.show_synced:
        print 'Congrats. Everything\'s in sync!'

if __name__ == '__main__':
    parser = OptionParser(usage='usage: %prog [branch]')
    parser.add_option('--no-color', action='store_false',
                      dest='colored', default=True)
    parser.add_option('-s', '--synced', action='store_true',
                      dest='show_synced', default=False,
                      help='show synced branches too')
    (opts, args) = parser.parse_args()
    if len(args) == 1:
        ref = args[0]
    elif not args:
        ref = get_active_branch()
    else:
        parser.print_usage()
        sys.exit(1)
    main(ref, opts)
