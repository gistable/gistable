#!/usr/bin/env python
""" What's the fastest way to initialize a 2-D array? """

import time

N = 1000

WIDTH, HEIGHT = N, N


class Path(object):
    def __init__(self, i, j):
        self.i, self.j = i, j


def try1():
    grid = [
        [Path(i, j) for j in range(HEIGHT)]
        for i in range(WIDTH)
    ]


def try2():
    grid = []
    for i in range(WIDTH):
        grid.append([])
        for j in range(HEIGHT):
            grid[i].append(Path(i, j))


def try3():
    grid = []
    for i in range(WIDTH):
        grid.append([Path(i, j) for j in range(HEIGHT)])


if __name__ == '__main__':
    start = time.time()
    try1()
    print "try1", time.time() - start, "seconds"

    start = time.time()
    try2()
    print "try2", time.time() - start, "seconds"

    start = time.time()
    try3()
    print "try3", time.time() - start, "seconds"
