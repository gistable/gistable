#!/usr/bin/env python
# -*- coding: utf-8  -*-
"""Clean up the git branches by removing branches whose change-id got merged."""
from __future__ import unicode_literals

import argparse
import collections
import itertools
import json
import re
import subprocess
import sys

if sys.version_info[0] > 2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


class Commit(object):

    def __init__(self, commit_hash, change_id):
        self.commit_hash = commit_hash
        self.change_id = change_id

    @classmethod
    def parse_message(cls, message):
        message = message.splitlines()
        commit_hash = message[0][len('commit '):]
        # skip header (4 lines) and reversed order
        message = message[:3:-1]
        # find first change-id
        change_id = None
        for line in message:
            if not line:
                break
            match = re.match('^ *Change-Id: (I[0-9A-Fa-f]{40})$', line)
            if match:
                if change_id:
                    print('Found multiple Change-IDs in commit message of '
                          '"{0}".'.format(commit_hash))
                else:
                    change_id = match.group(1)
        if not change_id:
            print('No Change-IDs found in commit message of '
                  '"{0}".'.format(commit_hash))
        return cls(commit_hash, change_id)


def exec_proc(*args, **kwargs):
    kwargs.setdefault('stdout', subprocess.PIPE)
    kwargs.setdefault('stderr', subprocess.STDOUT)
    proc = subprocess.Popen(args, **kwargs)
    out, err = proc.communicate()
    if sys.version_info[0] >= 3:
        out = out.decode("utf8")
    return out


def ssh_query(change_ids, additional_parameter):
    params = ['OR'] * (len(change_ids) * 2 - 1)
    params[0::2] = change_ids
    params = ['ssh', '-p', port, host, 'gerrit', 'query',
              '--format=JSON'] + list(additional_parameter) + params
    data = {}
    for line in exec_proc(*params).splitlines()[:-1]:
        status = json.loads(line)
        data[status['id']] = status
    return data


NEVER_DELETE = 0
ALWAYS_ASK = 1
NOT_REVIEW_ASK = 2
ALWAYS_DELETE = 3

parser = argparse.ArgumentParser()
parser.add_argument('--master-branch', default='master')
parser.add_argument('--remote', default='gerrit')
delete_mode = parser.add_mutually_exclusive_group()
delete_mode.add_argument('--always-delete', dest='delete_mode', action='store_const',
                    const=ALWAYS_DELETE)
delete_mode.add_argument('--not-review-ask', dest='delete_mode', action='store_const',
                    const=NOT_REVIEW_ASK)
delete_mode.add_argument('--always-ask', dest='delete_mode', action='store_const',
                    const=ALWAYS_ASK)
online_mode = parser.add_mutually_exclusive_group()
online_mode.add_argument('--load-additional-data', '-L', dest='online', action='store_const', const=True)
online_mode.add_argument('--offline', dest='online', action='store_const', const=False)

args = parser.parse_args()
if args.delete_mode is None:
    args.delete_mode = NEVER_DELETE

if args.online is not False:
    url = urlparse(exec_proc(
        'git', 'config', 'remote.{0}.url'.format(args.remote)).strip())
    host = '{0}@{1}'.format(url.username, url.hostname)
    port = str(url.port)

branches = []
git_branch_output = exec_proc('git', 'branch', '--no-color')
# remove the '  ' or '* ' in front of the list
branches = set(branch[2:] for branch in git_branch_output.splitlines())
if args.master_branch not in branches:
    print('The master branch "{0}" was not found.'.format(args.master_branch))
    sys.exit(1)

# Don't scan the master branch
branches.difference_update([args.master_branch])
branches = sorted(branches)

change_ids = set()
branch_ids = {}
for branch in branches:
    # get newest change-id
    message = exec_proc('git', 'log', '--pretty=medium', '--no-color', '-n', '1', branch)
    commit = Commit.parse_message(message)
    if commit.change_id:
        change_ids.add(commit.change_id)
    else:
        print('Branch "{0}" is going to be skipped.'.format(branch))
    branch_ids[branch] = commit

print('Found {0} branch(es) and {1} change ids'.format(len(branches), len(change_ids)))
if change_ids:
    if args.online is not False:
        print('Query server for {0} change id(s)…'.format(len(change_ids)))
        change_id_data = ssh_query(change_ids, [])
        open_change_ids = set(change_id for change_id, status in change_id_data.items()
                              if status['open'])
        if args.online is True and open_change_ids:
            print('Query server for additional data of {0} change '
                  'id(s)…'.format(len(open_change_ids)))
            change_id_data.update(ssh_query(open_change_ids, ['--patch-sets']))
    else:
        change_id_data = {}
        for change_id in change_ids:
            messages = exec_proc(
                'git', 'log', '--pretty=medium', '--no-color',
                '--grep=Change-Id: {0}'.format(change_id), args.master_branch)
            parts = re.split('commit ([0-9a-f]{40})', messages)
            commits = [None] * (len(parts) // 2)
            for i in range(len(commits)):  # parts is always #commits*2 + 1
                commits[i] = parts[i * 2 + 1] + parts[(i + 1) * 2]
            assert(None not in commits)
            for commit_entry in commits:
                commit = Commit.parse_message(commit_entry)
                if commit.change_id == change_id:
                    change_id_data[change_id] = {'open': False,
                                                 'status': 'MERGED'}
                    break
            else:
                change_id_data[change_id] = {'open': True}
            if len(change_id_data) % 10 == 0 and len(change_id_data) < len(change_ids):
                print('Process {0}th entry.'.format(len(change_id_data)))
else:
    change_id_data = {}

for branch in branches:
    commit = branch_ids[branch]
    status = change_id_data.get(commit.change_id)
    if status and not status['open']:
        if args.delete_mode is NEVER_DELETE:
            print('[X] Branch "{0}" got closed: {1}'.format(branch, status['status']))
        else:
            assert(args.delete_mode > 0)
            delete = args.delete_mode is ALWAYS_DELETE or (args.delete_mode is NOT_REVIEW_ASK and branch.startswith('review/'))
            if args.delete_mode is ALWAYS_ASK or not delete:
                answer = None
                while answer not in ['y', 'n']:
                    answer = input('Delete branch "{0}" [y/n]?'.format(branch)).lower()
                delete = answer == 'y'
            if not delete:
                print('[N] Branch "{0}" got closed but not deleted: {1}'.format(branch, status['status']))
            else:
                print('[D] Branch "{0}" got closed and deleted: {1}'.format(branch, status['status']))
                print(exec_proc('git', 'branch', '-D', branch).rstrip('\n'))
    elif not status:
        print('[!] Branch "{0}" was not submitted.'.format(branch))
    else:
        if 'patchSets' in status:
            updated = None
            for number, patch_set in enumerate(status['patchSets'], 1):
                assert(number == int(patch_set['number']))
                if updated:
                    updated = False
                    break
                if patch_set['revision'] == commit.commit_hash:
                    updated = True
        else:
            updated = True
        if updated:
            print('[ ] Branch "{0}" did not get merged.'.format(branch))
        elif updated is False:
            print('[U] Branch "{0}" could be updated.'.format(branch))
        else:
            print('[¦] Branch "{0}" is not a patch set revision.'.format(branch))
