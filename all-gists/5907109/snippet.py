__author__ = 'schwa'

import os
import subprocess
import glob
from github import Github # pip install PyGithub
from bitbucket.bitbucket import Bitbucket # pip install --user bitbucket-api

GH_USERNAME = 'jwight@mac.com'
GH_PASSWORD = '1234'

BB_USERNAME = 'jwight@mac.com'
BB_PASSWORD = '5678'

## Set up
d = os.path.expanduser('~/Desktop/Private Repos')
if not os.path.exists(d):
    os.makedirs(d)
os.chdir(d)

## Get list of all your github private repos.
## By default we filter out public repos and repos where you are not the owner. You can change this.
g = Github(GH_USERNAME, GH_PASSWORD)
theRepos = []
for repo in g.get_user().get_repos():
    if not repo.private:
        continue
    if repo.owner.name != g.get_user().name:
        continue
    theRepos.append((repo.name, repo.clone_url))

### CLOWN ALL THE THIGNS
for theName, theCloneURL in theRepos:
    print theName
    subprocess.check_call(['git', 'clone', theCloneURL, theName])

### Go through all the cloned directories, create a bitbucket repo and then push them
### If the repo already exists on github this will skip it.
bb = Bitbucket(BB_USERNAME, BB_PASSWORD, 'private_slug')
for name in glob.iglob('*'):
    print name
    result, r = bb.repository.create(name, scm='git', private=True)
    if not result:
        print 'Could not create repo, skipping'
        continue
    push_url = 'git@bitbucket.org:{owner}/{name}.git'.format(owner = r['owner'], name = r['name'])
    os.chdir(name)
    subprocess.check_call(['git', 'remote', 'set-url', 'origin', push_url])
    subprocess.check_call(['git', 'push'])
    os.chdir(d)
