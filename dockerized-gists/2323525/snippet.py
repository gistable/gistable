"""
This snippet shows how to listen for the SIGTERM signal on Unix and execute a
simple function open receiving it.

To test it out, uncomment the pid code and kill the process with:
    
    $ kill -15 pid
"""
import signal
import sys


# import os
# pid = os.getpid()
# print pid


def handler(signum, frame):
    print 'Shutting down...'
    sys.exit(1)


signal.signal(signal.SIGTERM, handler)