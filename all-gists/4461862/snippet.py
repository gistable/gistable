#!/usr/bin/env python

# requirements: GitPython
# version 0.1

import git
import os
import sys


def get_branch():
    """
    Get current branch with GitPython
    """
    path = os.getcwd()
    repo = git.Repo(path)
    return repo.head.reference.name


def prepare_commit_msg():
    """
    - Prepend "<branch name>, "
    """
    branch = get_branch()
    msg = "{0}, ".format(branch.lower().capitalize())
    # for prepare-commit-msg the second parameter
    # is the path to commit message
    path = sys.argv[1]
    try:
        with open(path, 'w') as f:
            content = f.read()
            f.write("{0}{1}".format(msg, content))
    except:
        pass

if __name__ == '__main__':
    prepare_commit_msg()