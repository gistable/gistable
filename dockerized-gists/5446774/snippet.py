#!/usr/bin/env python
"""
piphub - shortcut for user-only editable install from GitHub

usage:

    piphub org[/repo] [name]
    
`name` only needs to be specified if it differs from `repo`.
If the organization, repo, and name all have the same value (e.g. ipython),
then you can just specify the one name:

    piphub ipython

"""

import os
import sys
from subprocess import check_call

# the source-dir, where you keep your git repos
SRC = os.path.expanduser('~/dev/py')

def main(org, repo, name):
    """docstring for main"""
    if not os.path.exists(SRC):
        os.makedirs(SRC)
    url = "git+https://github.com/{org}/{repo}#egg={name}".format(**locals())
    cmd = ['pip', 'install', '--user', '--src', SRC, '-e' , url]
    check_call(cmd)
    

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print __doc__
    else:
        repo = sys.argv[1]
    
    if '/' in repo:
        org, repo = repo.split('/')
    else:
        org = repo
    
    if len(sys.argv) >= 3:
        name = sys.argv[2]
    else:
        name = repo
    
    main(org, repo, name)
