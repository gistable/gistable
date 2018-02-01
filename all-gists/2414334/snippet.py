# sshtail.py
# A script to tail a file across many systems at once
# Author: Luke Macken <lmacken@redhat.com>
# License: GPLv3+

import getpass
import subprocess

servers = ['app1', 'app2', 'app3', 'app4', 'app5', 'app6', 'app7']
logfile = '/var/log/httpd/access_log'
cmd = 'ssh -t -t -t %s sudo -S tail -f ' + logfile
processes = []
password = getpass.getpass()

for server in servers:
    p = subprocess.Popen(cmd % server, shell=True, stdin=subprocess.PIPE)
    p.stdin.write('%s\n' % password)
    p.stdin.close()
    processes.append(p)

try:
    while True:
        raw_input()
except:
    for p in processes:
        p.terminate()
    for p in processes:
        p.wait()