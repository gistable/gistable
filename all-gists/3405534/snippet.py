#!/usr/bin/env python

import os
import urllib2
import json
import subprocess

user=None
repo=None

github_cmd="git config --get remote.github.url".split(" ")
origin_cmd="git config --get remote.origin.url".split(" ")
# we want to determine the user / repository name
# my convention is that my own projects use 'github' as the remote
# origin when I created it. And, obviously, a clone will use 'origin'.
# so try them each
try:
    github = subprocess.check_output(github_cmd).strip()
    user, repo = github.split('/')[-2:]
    user = user.lstrip('git@github.com:')
    repo = repo.rstrip('.git')
except subprocess.CalledProcessError:
    pass  # ok, so no remote called 'github', let's try origin

if user is None and repo is None:
    try:
        origin = subprocess.check_output(origin_cmd).strip()
        user, repo = origin.split('/')[-2:]
        repo = repo.rstrip('.git')
    except subprocess.CalledProcessError:
        print("Could not determine user or repo.")
        os.exit(-1)

github_url='https://api.github.com/repos/%s/%s/forks'
resp = urllib2.urlopen(github_url % (user, repo))
if resp.code == 200:
    content = resp.read()
    data = json.loads(content)
    for remote in data:
        remote_add_cmd="git remote add %s %s" % (remote['owner']['login'], remote['clone_url'])
        print remote_add_cmd
        subprocess.call(remote_add_cmd.split(" "))
fetch_all_cmd="git fetch --all"
print fetch_all_cmd
subprocess.call(fetch_all_cmd.split(" "))
