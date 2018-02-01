#!/usr/bin/env python3
# coding: utf-8

from random import choice

def make_board(size):
    return { (x, y):choice('NSEW') for x in range(size) for y in range(size) }

def random_square(board):
    return choice(list(board.keys()))

def directions(board, start):
    p = start
    while p in board:
        yield board[p]
        p = next_position(board[p], p[0], p[1])

def next_position(d, x, y):
    if   d == 'N': return x, y + 1
    elif d == 'S': return x, y - 1
    elif d == 'E': return x + 1, y
    elif d == 'W': return x - 1, y

def positions(dirs):
    x, y = 0, 0
    for d in dirs:
        x, y = next_position(d, x, y)
        yield x, y

def speedy(things):
    while True:
        _ = next(things)
        yield next(things)

def does_halt(board, start):
    slow = positions(directions(board, start))
    fast = speedy(positions(directions(board, start)))
    for f, s in zip(fast, slow):
        if f == s: return False # Looped.
    return True # Fell off the end

if __name__ == '__main__':

    from sys import argv

    size  = int(argv[1])
    board = make_board(size)
    start = random_square(board)

    for x in range(size):
        row = ((x, y) for y in range(size))
        print(' '.join(board[c].upper() if c == start else board[c].lower() for c in row))

    print(does_halt(board, start))
