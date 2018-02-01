#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import check_call
from subprocess import check_output
from subprocess import CalledProcessError

# First prune the list
check_call(['git', 'remote', 'prune', 'origin'])

# Second get all of our remote branches
remote_branches_output = check_output(['git', 'branch',  '-r'])

# Get all of our local branches
local_branches_output = check_output(['git', 'branch'])

# Get our remote branches into a list we can iterate over
remote_branches_list = remote_branches_output.split('\n')
remote_branches_list = [branch.strip() for branch in remote_branches_list]
remote_branches_list = [branch.replace('origin/', '') for branch in remote_branches_list]

# Get our local branches to compare with
local_branches_list = local_branches_output.split('\n')
local_branches_list = [branch.strip() for branch in local_branches_list]

# For each local branch not in the remote delete it.
branches_not_deleted = []
for local_branch in local_branches_list:
    if local_branch not in remote_branches_list and '*' not in local_branch:
        try:
            check_call(['git', 'branch', '-d', local_branch])
            continue
        except CalledProcessError:
            pass
    branches_not_deleted.append(local_branch)

print u"Branches not deleted: {0}".format(str(branches_not_deleted))
