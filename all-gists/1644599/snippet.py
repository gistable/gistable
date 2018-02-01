#!/usr/bin/env python
import os, subprocess

uid, gid = 5, 60

def preexec_fn():
    os.setgid(uid)
    os.setuid(gid)

cmd = ['uname', '-a']

process = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           preexec_fn=preexec_fn)

outs, errs = process.communicate()
print "process return code:", process.returncode
print "stderr:", errs
print "stdout:", outs
