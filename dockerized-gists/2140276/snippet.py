"""Python implementation of Conway's Game of Life

Somewhat inspired by Jack Diederich's talk `Stop Writing Classes`
http://pyvideo.org/video/880/stop-writing-classes

Ironically, as I extended the functionality of this module it seems obvious
that the next step would be to refactor board into a class with advance and
constrain as methods and print_board as __str__.
"""

import sys
import time


GLIDER = {
    (2, 2),
    (1, 2),
    (0, 2),
    (2, 1),
    (1, 0),
}


def neighbors(cell, distance=1):
    """Return the neighbors of cell."""
    x, y = cell
    r = xrange(0 - distance, 1 + distance)
    return ((x + i, y + j) # new cell offset from center
            for i in r for j in r # iterate over range in 2d
            if not i == j == 0) # exclude the center cell


def advance(board):
    """Advance the board one step and return it."""
    new_board = set()
    for cell in board:
        cell_neighbors = set(neighbors(cell))
        # test if live cell dies
        if len(board & cell_neighbors) in [2, 3]:
            new_board.add(cell)
        # test dead neighbors to see if alive
        for n in cell_neighbors:
            if len(board & set(neighbors(n))) is 3:
                new_board.add(n)
    return new_board


def print_board(board, size=None):
    sizex = sizey = size or 0
    for x, y in board:
        sizex = x if x > sizex else sizex
        sizey = y if y > sizey else sizey
    for i in xrange(sizex + 1):
        for j in xrange(sizey + 1):
            sys.stdout.write(' x ' if (i, j) in board else ' . ')
        print


def constrain(board, size):
    return set(cell for cell in board if cell[0] <= size and cell[1] <= size)


def main(board, steps=75, size=20):
    for i in xrange(1, steps + 1):
        sys.stdout.write('\033[H')  # move to the top
        sys.stdout.write('\033[J')  # clear the screen
        print 'step:', i, '/', steps
        print_board(board, size)
        time.sleep(0.1)
        board = constrain(advance(board), size)


if __name__ == '__main__':
    main(GLIDER)
