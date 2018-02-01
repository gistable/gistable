#!/usr/bin/env python


def next_col(current, n=8):
    length = len(current)
    if length == n:
        return
    dangerous = current + [item for l in [(val + length - i, val - length + i) for i, val in enumerate(current)] for item in l if item >= 0 and item <= n]
    for i in range(n):
        if i not in dangerous:
            yield i


def queens(n=8, columns=[]):
    if len(columns) == n:
        yield columns
    for i in next_col(columns, n):
        appended = columns + [i]
        for c in queens(n, appended):
            yield c


if __name__ == '__main__':
    for solution in queens(8):
        print solution
