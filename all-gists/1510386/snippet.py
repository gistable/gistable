#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

Run forking multiprocess workers with emphasis's on running reliably long running processes, that
are for one or other reason prone to random crashing. Can be demonised with
http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/

"""

# Import
import os
import signal
from signal import SIGINT, SIGTERM
import time


def worker(num):
    """Worker simulating crash 5'th worker constantly crash"""
    print 'A new child ',  os.getpid( )
    while 1:
        time.sleep(3)
        3/num

def signalHandler(s, f):
    """Dummy function for SIGTERM trapping"""
    pass

def main():
    """Main function start and stop workers"""
    jobs = []
    nums = [1, 2, 3, 4, 0]
    for x in nums:
        newpid = os.fork()
        if newpid:
            jobs.append(newpid)
            pids = (os.getpid(), newpid)
            print "parent: %d, child: %d" % pids
        else:
            while 1:
                # if worker crashes start it again
                try:
                    worker(x)
                except Exception:
                    pass
                except (KeyboardInterrupt, SystemExit):
                    os._exit(0)
    # Register signal handler, without this OSError is not registered as exception
    signal.signal(SIGTERM, signalHandler)
    try:
        # this part is newer reached unless interrupted
        os.waitpid(-1, 0)
    except (OSError, KeyboardInterrupt):
        print 'End closing workers'
    finally:
        # Kill child processes
        for pid in jobs:
            if os.path.exists("/proc/%s" % pid):
                os.kill(pid, SIGINT)

if __name__ == "__main__":
    main()
