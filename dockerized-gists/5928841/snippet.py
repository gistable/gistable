import os

import tag #pip install --user git+https://github.com/schwa/half-moon-tagging.git
import re
import subprocess
import sys
import envoy

path = '/Users/schwa/Development/Source/Projects'

N = 0
for root, dirs, files in os.walk(path):
    tags = set()

    if '.git' not in dirs:
        if len(root[len(path) + 1:].split('/')) == 2:
            del dirs[:]
            tags.add('temp-no-git')
    else:
        #print N, root
        N += 1

        #print root
        os.chdir(root)
        s = subprocess.check_output(['git', 'remote', '-v'])
        s = s.strip()
        s = s.split('\n')

        #if len(s) not in (0, 1, 2):
        #    print s
        match = re.match(r'^(origin)\t(.+) \((fetch|push)\)', s[0])
        if match:
            remote = match.group(1)
            url = match.group(2)
            thePatterns = [
                r'git://(.+)/(.+)/(.+).git',
                r'https://(.+)/(.+)/(.+).git',
                r'git@(.+):(.+)/(.+).git'
                ]
            for thePattern in thePatterns:
                match = re.match(thePattern, url)
                if match:
                    break
            if match:
                service = match.group(1)
                owner = match.group(2)
                name = match.group(3)

                #tags.add('temp-service-name:{}'.format(service))
                #if name.lower() != os.path.split(root)[1].lower():
                #    tags.add('temp-name-mismatch')
#                    tags.add('temp-remote-name:{}'.format(name))

                if owner not in ('schwa', 'TouchCode'):
#                    tags.add('temp-owner:{}'.format(match.group(2)))
                    tags.add('temp-strange-owner')
            else:
                tags.add('temp-strange-origin')

            ### Uncomment follow to check for existence of remote repo
            #r = envoy.run('git ls-remote')
            #if r.status_code:
            #    tags.add('temp-remote-missing')
        else:
            tags.add('temp-local-only')

        r = envoy.run('git log --branches --not --remotes --oneline')
        r = r.std_out.strip().split('\n')
        if r and r != ['']:
            tags.add('temp-outgoing')

        r = envoy.run('git status --porcelain')
        r = r.std_out.split('\n')
        if r and r != ['']:
            tags.add('temp-dirty')


        del dirs[:]

    if tags:
        print root
        print '\t{}'.format(list(tags))

    if tags:
        tag.add_tags(root, list(tags))

