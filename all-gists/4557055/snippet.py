#!/usr/bin/env python
import subprocess
import shlex
import sys
import os
import operator

gitdir,workdir=map(os.path.realpath,sys.argv[1:3])
os.chdir(gitdir)
proc=subprocess.Popen(shlex.split('git rev-list --all'),stdout=subprocess.PIPE)
shas,err=proc.communicate()
shas=shas.split()
head=shas[0]
data={}
for sha1 in shas:
    subprocess.Popen(shlex.split('git checkout {s}'.format(s=sha1)),
                          stderr=open('/dev/null')).wait()
    proc=subprocess.Popen(shlex.split('diff {g} {w}'.format(g=gitdir,w=workdir)),
                          stdout=subprocess.PIPE)
    out,err=proc.communicate()
    distance=len(out)
    data[sha1]=distance
answer=min(data.items(),key=operator.itemgetter(1))[0]
print('closest match: {s}'.format(s=answer))
subprocess.Popen(shlex.split('git checkout {h}'.format(h=head)),
                 stderr=open('/dev/null')).wait()
