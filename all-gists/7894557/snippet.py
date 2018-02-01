#!/usr/bin/env python

import subprocess
import time
import re
import os
import sys

# launch the server and get the jobid

ipy_notebook_command = ['bsub', '-q short', '-W 720', 'ipython notebook --pylab']
p = subprocess.Popen(ipy_notebook_command, stdout=subprocess.PIPE)
out, err = p.communicate()
print out

job_id = out.split('<')[1].split('>')[0]

# use bjobs to get the node the server is running on
server = None
print 'querying queue for job info.',
while server is None:
    bjob_command = ['bjobs', '-l', job_id]
    p = subprocess.Popen(bjob_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if err is not None:
        print '.',
        sys.stdout.flush()

    m = re.search('Started on <(.*)>', out)
    try:
        server =  m.groups()[0]
    except AttributeError:
        time.sleep(1)

# launch ssh to connect to the node with a tunnel
print ''
print 'server launched on '+server+', opening ssh connection with tunnel.'
os.system('ssh -L 8888:127.0.0.1:8888 '+server)  # using os.system to fork

# when we exit the ssh connection, kill the server

bkill_command = ['bkill', job_id]
p = subprocess.Popen(bkill_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()
print out
