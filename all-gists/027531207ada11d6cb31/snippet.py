#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# pylint: disable=invalid-name,missing-docstring,bad-builtin
from sys import stdin
from collections import deque

def main():
    def steps(a, b, c):
        queue = deque([(0, 0), (-1, -1)])
        visited = set()
        count = 0
        while len(queue) > 1:
            x, y = queue.popleft()
            if x == -1 == y:
                count += 1
                queue.append((-1, -1))
                continue
            if x == c or y == c:
                return count
            if (x, y) in visited:
                continue
            visited.add((x, y))
            for p in [
                    (0, y), (x, 0), (a, y), (x, b),
                    (x - min(x, b - y), y + min(x, b - y)),
                    (x + min(y, a - x), y - min(y, a - x))]:
                if p not in visited and p != (x, y):
                    queue.append(p)
        return -1

    dstream = map(int, stdin.readlines())
    for t in xrange(dstream[0]):
        a, b, c = dstream[3*t + 1], dstream[3*t + 2], dstream[3*t + 3]
        print steps(a, b, c)


main()
