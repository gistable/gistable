#!/usr/bin/python
#Copyright (c) 2012 Kyle Harrigan
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

# Import MKS history into GIT
# Meant to be used with fast-import
#
# Currently imports checkpoints only... 
# kyle.harrigan@gtri.gatech.edu

import os
from subprocess import Popen
from subprocess import PIPE, STDOUT
import time
import sys
import csv
import re
from datetime import datetime

def export_data(string):
    print 'data %d\n%s' % (len(string), string)

def inline_data(filename, code = 'M', mode = '644'):
    content = open(filename, 'r').read()
    print "%s %s inline %s" % (code, mode, filename)
    export_data(content)

pipe = Popen('si viewprojecthistory --project="%s"' % sys.argv[1], shell=True, bufsize=1024, stdin=PIPE, stdout=PIPE, close_fds=True)
versions = pipe.stdout.read().split('\n')
versions = versions[1:]
version_re = re.compile('[0-9]([\.0-9])+')

revisions = []
for version in versions:
    match = version_re.match(version)
    if match:
        version_cols = version.split('\t')
        revision = {}
        revision["number"] = version_cols[0]
        revision["author"] = version_cols[1]
        revision["seconds"] = int(time.mktime(datetime.strptime(version_cols[2], "%b %d, %Y %I:%M:%S %p").timetuple()))
        revision["description"] = version_cols[6]
        revisions.append(revision)        

if 0:
    print revisions[0]
    sys.exit(0)
    
revisions.reverse() # Old to new
ct = 0
for revision in revisions:
    ct += 1
    # Create a build sandbox for the version
    os.system('si createsandbox --populate -R --project="%s" --projectRevision=%s tmp' % (sys.argv[1], revision["number"]))
    #print 'DEBUG: %s' % revision
    #"si co -R --nolock --overwriteChanged -r 1.3RC1 --filter=label:1.3RC1"
    #os.system("si co --quiet -u -Y -r %s" % (revision["number"]))
    #pipe.wait()
    os.chdir('tmp')
    print 'commit refs/heads/main'
    print 'mark :%d' % ct
    print 'committer %s <> %d -0400' % (revision["author"], revision["seconds"])
    export_data(revision["description"])
    print 'deleteall'
    tree = os.walk('.')
    for dir in tree:      
        for filename in dir[2]:
            if (dir[0] == '.'):
                fullfile = filename
            else:
                fullfile = os.path.join(dir[0], filename)[2:]

	    if (fullfile[0:4] == ".git"):
                continue
            if (fullfile.find('.pj') != -1):
                continue
            if (fullfile.find('mks_git_checkpoints') != -1):
                continue
            inline_data(fullfile)
    # Drop the sandbox
    os.chdir("..")
    shortname=sys.argv[1].replace('"', '').split('/')[-1]
    os.system("si dropsandbox -Y -f --delete=all tmp/%s" % shortname)
