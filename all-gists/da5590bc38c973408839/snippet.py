#!/usr/bin/env python3

# Copyright 2014 Brett Slatkin, Pearson Education Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
======================================================
John Conway's Game of Life implemented with coroutines
======================================================

by Brett Slatkin

This script was refactored by Luciano Ramalho from code listed in Item
40 of Brett Slatkin's excellent book "Effective Python: 59 Specific Ways
to Write Better Python".

The original code is published on Github under the Apache 2.0 license:

https://github.com/bslatkin/effectivepython/blob/master/example_code/item_40.py


The refactoring included:

- replacing the top-level testing code with doctests;

- changing the ``Grid.query`` method to ``Grid.__getitem__``, taking a
  tuple of coordinates as argument;

- similarly, changing the ``Grid.assign`` method to ``Grid.__setitem__``;


Running this script produces no output. To run the doctests, use::

    $ python3 -m doctest coro_life.py


No output will be generated if all doctests pass. To see doctest output,
use::

    $ python3 -m doctest coro_life.py -v


--------------------------------------------
Doctests for specific components of the code
--------------------------------------------


Drive ``count_neighbors``
=========================

Drive the ``count_neighbors`` coroutine with fake data::

    >>> it = count_neighbors(10, 5)
    >>> next(it)  # Get the first query, for q1
    Query(y=11, x=5)
    >>> it.send(ALIVE)  # Send q1 state, get q2
    Query(y=11, x=6)
    >>> it.send(ALIVE)  # Send q2 state, get q3
    Query(y=10, x=6)
    >>>  # Send q3 ... q7 states, get q4 ... q8
    >>> [it.send(state) for state in (EMPTY)*5]  # doctest: +ELLIPSIS
    [Query(y=9, x=6), Query(y=9, x=5), ..., Query(y=11, x=4)]
    >>> try:
    ...     it.send(EMPTY)  # Send q8 state, drive coroutine to end
    ... except StopIteration as e:
    ...     count = e.value  # Value from return statement
    ...
    >>> count
    2


Drive ``step_cell``
===================

Drive the ``step_cell`` coroutine with fake data::

    >>> it = step_cell(10, 5)
    >>> next(it)  # Initial location query
    Query(y=10, x=5)
    >>> [it.send(st) for st in (ALIVE)*5 + (EMPTY)*3]   # doctest: +ELLIPSIS
    [Query(y=11, x=5), Query(y=11, x=6), ... Query(y=11, x=4)]
    >>> it.send(EMPTY)  # Send q8 state, get game decision
    Transition(y=10, x=5, state='-')


Test ``Grid``
=============

Put a glider in a 5x9 grid:

    >>> grid = Grid(5, 9)
    >>> grid[0, 3] = ALIVE
    >>> grid[1, 4] = ALIVE
    >>> grid[2, 2] = ALIVE
    >>> grid[2, 3] = ALIVE
    >>> grid[2, 4] = ALIVE
    >>> print(grid)
    ---*-----
    ----*----
    --***----
    ---------
    ---------
    <BLANKLINE>


Run the game for 5 generations
==============================

Test ``ColumnPrinter``, ``simulate`` and ``live_a_generation``::

    >>> columns = ColumnPrinter()
    >>> sim = simulate(grid.height, grid.width)
    >>> for i in range(5):
    ...     columns.append(str(grid))
    ...     grid = live_a_generation(grid, sim)
    ...
    >>> print(columns)  # doctest: +NORMALIZE_WHITESPACE
        0     |     1     |     2     |     3     |     4
    ---*----- | --------- | --------- | --------- | ---------
    ----*---- | --*-*---- | ----*---- | ---*----- | ----*----
    --***---- | ---**---- | --*-*---- | ----**--- | -----*---
    --------- | ---*----- | ---**---- | ---**---- | ---***---
    --------- | --------- | --------- | --------- | ---------


Introductory diagram
====================

The first Game of Life example in Item 40 of "Effective Python"
(with an added generation showing zero surviving cells)::

    >>> grid = Grid(5, 5)
    >>> grid[1, 1] = ALIVE
    >>> grid[2, 2] = ALIVE
    >>> grid[2, 3] = ALIVE
    >>> grid[3, 3] = ALIVE
    >>> columns = ColumnPrinter()
    >>> sim = simulate(grid.height, grid.width)
    >>> for i in range(6):
    ...     columns.append(str(grid))
    ...     grid = live_a_generation(grid, sim)
    ...
    >>> print(columns)  # doctest: +NORMALIZE_WHITESPACE
      0   |   1   |   2   |   3   |   4   |   5
    ----- | ----- | ----- | ----- | ----- | -----
    -*--- | --*-- | --**- | --*-- | ----- | -----
    --**- | --**- | -*--- | -*--- | -**-- | -----
    ---*- | --**- | --**- | --*-- | ----- | -----
    ----- | ----- | ----- | ----- | ----- | -----


Blinker demo
============

The blinker is the simplest oscillator::

    >>> grid = Grid(5, 5)
    >>> for i in range(1, 4):
    ...     grid[2, i] = ALIVE
    ...
    >>> columns = ColumnPrinter()
    >>> sim = simulate(grid.height, grid.width)
    >>> for i in range(8):
    ...     columns.append(str(grid))
    ...     grid = live_a_generation(grid, sim)
    ...
    >>> print(columns)  # doctest: +NORMALIZE_WHITESPACE
      0   |   1   |   2   |   3   |   4   |   5   |   6   |   7
    ----- | ----- | ----- | ----- | ----- | ----- | ----- | -----
    ----- | --*-- | ----- | --*-- | ----- | --*-- | ----- | --*--
    -***- | --*-- | -***- | --*-- | -***- | --*-- | -***- | --*--
    ----- | --*-- | ----- | --*-- | ----- | --*-- | ----- | --*--
    ----- | ----- | ----- | ----- | ----- | ----- | ----- | -----

"""


from collections import namedtuple

ALIVE = '*'
EMPTY = '-'
TICK = object()

Query = namedtuple('Query', 'y x')

Transition = namedtuple('Transition', 'y x state')


def count_neighbors(y, x):
    n_ = yield Query(y + 1, x + 0)  # North
    ne = yield Query(y + 1, x + 1)  # Northeast
    e_ = yield Query(y + 0, x + 1)  # East
    se = yield Query(y - 1, x + 1)  # Southeast
    s_ = yield Query(y - 1, x + 0)  # South
    sw = yield Query(y - 1, x - 1)  # Southwest
    w_ = yield Query(y + 0, x - 1)  # West
    nw = yield Query(y + 1, x - 1)  # Northwest
    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0
    for state in neighbor_states:
        if state == ALIVE:
            count += 1
    return count


def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY     # Die: Too few
        elif neighbors > 3:
            return EMPTY     # Die: Too many
    else:
        if neighbors == 3:
            return ALIVE     # Regenerate
    return state


def step_cell(y, x):
    state = yield Query(y, x)
    neighbors = yield from count_neighbors(y, x)
    next_state = game_logic(state, neighbors)
    yield Transition(y, x, next_state)


def simulate(height, width):
    while True:
        for y in range(height):
            for x in range(width):
                yield from step_cell(y, x)
        yield TICK


class Grid(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def __str__(self):
        output = ''
        for row in self.rows:
            for cell in row:
                output += cell
            output += '\n'
        return output

    def __getitem__(self, position):
        y, x = position
        return self.rows[y % self.height][x % self.width]

    def __setitem__(self, position, state):
        y, x = position
        self.rows[y % self.height][x % self.width] = state


def live_a_generation(grid, sim):
    progeny = Grid(grid.height, grid.width)
    item = next(sim)
    while item is not TICK:
        if isinstance(item, Query):
            state = grid[item.y, item.x]
            item = sim.send(state)
        else:  # Must be a Transition
            progeny[item.y, item.x] = item.state
            item = next(sim)
    return progeny


class ColumnPrinter(object):
    def __init__(self):
        self.columns = []

    def append(self, data):
        self.columns.append(data)

    def __str__(self):
        row_count = 1
        for data in self.columns:
            row_count = max(row_count, len(data.splitlines()) + 1)
        rows = [''] * row_count
        for j in range(row_count):
            for i, data in enumerate(self.columns):
                line = data.splitlines()[max(0, j - 1)]
                if j == 0:
                    rows[j] += str(i).center(len(line))
                else:
                    rows[j] += line
                if (i + 1) < len(self.columns):
                    rows[j] += ' | '
        return '\n'.join(rows)
