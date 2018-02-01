# You need gevent 1.0 and pyzmq 3.x
#
# pip install --user git://github.com/SiteSupport/gevent.git
# pip install --user pyzmq
#
import gevent
import zmq.green as zmq

import os, sys

ADDR = 'tcp://127.0.0.1:5555'

def run_parent():
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PUSH)
    sock.bind(ADDR)
    for i in range(10):
        sock.send('message: %d' % i)
        gevent.sleep(1)


def run_child(ident):
    # create a new context since we are forked in a new process
    ctx = zmq.Context()
    sock = ctx.socket(zmq.PULL)
    sock.connect(ADDR)

    while True:
        msg = sock.recv()
        print '%s: %s' % (ident, msg)


def fork_workers(num):
    pids = []
    for i in range(num):
        pid = gevent.fork()
        if pid == 0:
            run_child(os.getpid())
            sys.exit(0)
        else:
            pids.append(pid)
    return pids


pids = fork_workers(3)
print 'workers:', ', '.join('%d' % p for p in pids)

run_parent()

# not cool, workers should die themselves actually
for pid in pids:
    os.kill(pid, 15)
