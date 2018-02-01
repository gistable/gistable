#!/usr/bin/env python

import sys

from subprocess import Popen, PIPE, STDOUT

try:
    search = sys.argv[1]    
except:
    print "Need to enter a email or a part of an email"
    print " -- %s example.net" % sys.argv[0]
    sys.exit(2)

cmd = 'mailq'
p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
output = p.stdout.read()

emails = []
chunk = {"id": None, "reason": None, "to": None}
line_num = 1
for line in output.split("\n"):
    if line == "":
        emails.append(chunk)

        chunk = {"id": None, "reason": None, "to": None}
        line_num = 1
    else:
        if line_num == 1:
            chunk['id'] = line.split()[0]
        elif line_num == 2:
            chunk['reason'] = line
        elif line_num == 3:
            chunk['to'] = line.strip()

        line_num += 1

for email in emails:
    if email['to'] is None:
        continue

    if search in email['to']:
        cmd = "postsuper -d %s" % email['id']
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        print p.stdout.read()
