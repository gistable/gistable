#!/usr/bin/python
'''
A tidier version of this can be found here https://github.com/rwky/Compare-git-branches

Copyright (c) 2012 Rowan Wookey <admin@rwky.net>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
import sys, subprocess, getopt
opts, args = getopt.getopt(sys.argv[1:],"ha:b:t:")

for opt,arg in opts:
    if opt == '-h':
        print '''
        Usage:
        -h help
        -a the name of branch a
        -b the name of branch b
        -t how far back in time to go (passed to git log as --since)
        '''
        sys.exit();
    if opt == '-a':
        branchA = arg
    if opt == '-b':
        branchB = arg
    if opt == '-t':
        since = arg
if 'branchA' not in globals() or 'branchB' not in globals():
    print 'You must specify two branches with -a and -b'
    sys.exit(1)


cmd = ['git','log','--oneline','--no-merges']
if 'since' in globals():
    cmd.append('--since="%s"' % since)

branch1 = {}
branch2 = {}
branch1_output = subprocess.check_output(cmd+[branchA]);
branch1_lines = branch1_output.split('\n')
branch2_output = subprocess.check_output(cmd+[branchB]);
branch2_lines = branch2_output.split('\n')
if branch1_lines[-1] == '':
    branch1_lines.pop()
if branch2_lines[-1] == '':
    branch2_lines.pop()
i = 0
for line in branch1_lines:
    commit = line[:6]
    msg =  line[7:]
    diff = subprocess.check_output(['git', 'show', commit])
    p = subprocess.Popen(['git', 'patch-id'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    patch_id = p.communicate(input=diff)[0].split(' ')[0]
    branch1[patch_id] = [commit,msg]
    i+=1
    print '%s%%' % ((float(i)/float(len(branch1_lines)+len(branch2_lines)))*100)
for line in branch2_lines:
    commit = line[:6]
    msg =  line[7:]
    diff = subprocess.check_output(['git', 'show', commit])
    p = subprocess.Popen(['git', 'patch-id'], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    patch_id = p.communicate(input=diff)[0].split(' ')[0]
    branch2[patch_id] = [commit,msg]
    i+=1
    print '%s%%' % ((float(i)/float(len(branch1_lines)+len(branch2_lines)))*100)

print "Missing from %s" % branchA
for k in branch2.keys():
    if k not in branch1:
        c = branch2.get(k)
        print '%s %s' % (c[0],c[1])

print "Missing from %s" % branchB
for k in branch1.keys():
    if k not in branch2:
        c = branch1.get(k)
        print '%s %s' % (c[0],c[1])