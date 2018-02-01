#!/usr/bin/env python
import sys
import time
import signal
from subprocess import Popen, PIPE

dd = Popen(['dd'] + sys.argv[1:], stderr=PIPE)
while dd.poll() is None:
    time.sleep(.3)
    dd.send_signal(signal.SIGUSR1)
    while 1:
        l = dd.stderr.readline()
        if 'records in' in l:
            print l[:l.index('+')], 'records',
        if 'bytes' in l:
            print l.strip(), '\r',
            break
print dd.stderr.read(),
