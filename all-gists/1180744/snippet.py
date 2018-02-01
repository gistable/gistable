import gevent.monkey
gevent.monkey.patch_all()

import os
import sys
import fcntl
import gevent
from gevent.socket import wait_read

from redis import Redis

PID = os.getpid()

red = Redis('localhost')

def echo_stdin():
    # make stdin non-blocking
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    red.publish('echo', "[%i] joined" % (PID,))
    while True:
        wait_read(sys.stdin.fileno())
        l = sys.stdin.readline().strip()
        s = "[%i] %s" % (PID, l)
        # save to log
        red.rpush('echo_log', s)
        # publish message
        red.publish('echo', s)
        if l == 'quit':
            break

def handler():
    pubsub = red.pubsub()
    # first subscribe, then print log (no race condition this way)
    pubsub.subscribe('echo')
    # print log
    for line in red.lrange('echo_log', 0, -1):
        print '.', line
    # print channel
    for msg in pubsub.listen():
        print '>', msg['data']

gevent.spawn(handler)
gevent.spawn(echo_stdin).join()
