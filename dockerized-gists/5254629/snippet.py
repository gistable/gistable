#!/usr/bin/env pypy-c

from __future__ import print_function
import random
import math
import sys
import signal
import os
import time


MAX_DISTANCE = 100 ** 2


def calc(count, size):
    # a: [[priority, distance]]
    a = [[math.sqrt(random.randint(1, MAX_DISTANCE))] * 2 for _ in range(size)]
    for _ in range(count):
        a.sort()
        #print(a)
        mp = a[0][0] + 5
        i = 0
        for i in range(size):
            if a[i][0] <= mp:
                a[i][0] += a[i][1]
            else:
                break
        else:
            print("done, i = %d, %s" % (_, str(map(lambda x: round(x[1], 2), a))))
            return
        for j in range(i):
            if a[j][0] < a[i][0]:
                a[j][0] = a[i][0]
    print("failed, i = %d, %s" % (_, str(map(lambda x: x[1], a))))


if __name__ == '__main__':
    children = []
    for _ in range(4):
        # use as many children as our cpu cores to speedup
        pid = os.fork()
        if pid == 0:
            random.seed()  # otherwise all children will end up with the same a
            t1 = time.time()
            calc(100 * 1000 * 1000, 10)
            t2 = time.time()
            print("time cost:", t2 - t1)
            sys.exit(0)
        else:
            children.append(pid)

    try:
        try:
            while True:
                print(os.waitpid(-1, 0))
        except OSError:
            print("done")
    except KeyboardInterrupt:
        # kill all children or they become zombies that eat a lot cpu
        for pid in children:
            os.kill(pid, signal.SIGKILL)
