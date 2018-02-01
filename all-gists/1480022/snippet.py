#!/usr/bin/env python
# Git clone all my gists

import json
import urllib
from subprocess import call
from urllib import urlopen
import os
USER = os.environ['USER']

u = urlopen('https://gist.github.com/api/v1/json/gists/' + USER)
gists = json.load(u)['gists']

for gist in gists:
    call(['git', 'clone', 'git://gist.github.com/' + gist['repo'] + '.git'])
