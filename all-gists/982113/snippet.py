#!/usr/bin/env python
from gevent import sleep
import gevent
import sys

def x(i):
    sleep(int(i))
    print i

jobs = [gevent.spawn(x, i) for i in sys.argv[1:]]
gevent.joinall(jobs)
