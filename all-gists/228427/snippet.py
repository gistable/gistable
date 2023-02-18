#!/usr/bin/env python

'''
Takes a GitHub service hook POST and automatically updates the associated repo.
'''

__license__ = '''
Copyright 2009 Jake Wharton

hookpuller is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

hookpuller is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General
Public License along with hookpuller.  If not, see
<http://www.gnu.org/licenses/>.
'''

import json
import subprocess
import sys
import urllib

#Associate branch names with repo locations on disk
repos = {
  #'repository name': {
  #  'branch name': 'path on disk',
  #  ...
  #}
  #...
  'jakewharton.com': {
    'main': '/home/jakewharton/jakewharton.com/',
    'dev'   : '/home/jakewharton/dev.jakewharton.com/',
  }
}

#Read and load JSON from POST
data = json.loads(urllib.unquote(sys.stdin.read())[8:]) #8 = len('payload=')

#Get repo and branch that was committed to
repo   = data['repository']['name']
branch = data['ref'][11:] #11 = len('refs/heads/')

if repo in repos and branch in repos[repo]:
  #Execute pull in branch's associated directory
  subprocess.call(['git', 'pull', 'origin', branch], cwd=repos[repo][branch])