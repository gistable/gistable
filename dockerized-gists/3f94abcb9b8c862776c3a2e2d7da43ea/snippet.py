"""Calculate the average number of moves in a snakes and ladders game.

Because as a parent one gets roped into these board (boring?) games
every so often, and I wanted to calculate the average duration of a
snakes and ladders game. Turns out it's about 36 moves (though
admittedly that's for a single-player game). :-)

> python snakes_and_ladders.py
Played 10000 rounds, averaged 36.0559 moves, max 324 moves, took 0.508s
"""

from __future__ import division

import random
import time

try:
    range = xrange  # Make range a generator on Python 2.7
except NameError:
    pass


# Defines the snakes and ladders on the board. A low:high item
# represents a ladder going from low to high, whereas a high:low
# item represents a snake going from high to low.
SNAKES_LADDERS = {
    1: 38, 4: 14, 9: 31,
    16: 6,
    21: 42, 28: 84,
    36: 44,
    48: 26, 49: 11,
    51: 67, 56: 53,
    62: 19, 64: 60,
    71: 91, 80: 100,
    87: 24,
    93: 73, 95: 75, 98: 78,
}
MAX_SQUARE = 100
MAX_MOVES = 100000


def play_one():
    """Play one game and return the number of moves it took."""
    square = 0
    for num_moves in range(1, MAX_MOVES + 1):
        dice_roll = random.randrange(1, 7)
        square += dice_roll
        square = SNAKES_LADDERS.get(square, square)
        if square >= MAX_SQUARE:
            return num_moves
    return MAX_MOVES


def play_all(num_rounds):
    """Play num_rounds games and return tuple of (total, max, time)."""
    start_time = time.time()

    total_moves = 0
    max_moves = 0
    for _ in range(num_rounds):
        num_moves = play_one()
        total_moves += num_moves
        max_moves = max(max_moves, num_moves)

    elapsed_time = time.time() - start_time

    return (total_moves, max_moves, elapsed_time)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num-rounds', type=int, default=10000,
                        help='number of rounds (games) to play')
    args = parser.parse_args()

    total_moves, max_moves, elapsed_time = play_all(args.num_rounds)
    print('Played {} rounds, averaged {} moves, max {} moves, took {:.3f}s'.format(
        args.num_rounds,
        total_moves / args.num_rounds,
        max_moves,
        elapsed_time,
    ))
