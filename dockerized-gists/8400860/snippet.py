#!/usr/bin/env python

def cross(A, B):
    return [a + b for a in A for b in B]

digits = '123456789'
letters = 'ABCDEFGHI'
rows = letters
cols = digits

squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(r, c) for r in ['ABC', 'DEF', 'GHI'] for c in ['123', '456', '789']])

units = dict([(s, [u for u in unitlist if s in u]) for s in squares])
peers = dict([ (s, set(sum(units[s], [])) - set([s])) for s in squares ])

def solve(grid):
    grid = parse_grid(grid)
    values = dict([(s, digits) for s in squares])
    for s, v in grid.items():
        if v in digits and not assign(values, s, v):
            return False
    return values

# changed method
def assign(values, s, d):
    values[s] = d
    eliminate(values, s, d)
    return values

# changed method
def eliminate(values, s, d):
    for p in peers[s]:
        if len(values[p]) > 1:
            values[p] = values[p].replace(d, '')
            if len(values[p]) == 1:
                assign(values, p, values[p])
    return values

def search(values):
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in squares):
        return values
    n,s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(search(assign(values.copy(), s, d)) for d in values[s])

def some(seq):
    for e in seq:
        if e:
            return e
    else: False

def parse_grid(grid):
    return dict(zip(squares, grid))

def display(values):
    width = 1+max(len(values[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)

if __name__ == '__main__':
    hard1 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    hard2 = '.................................................................................'
    display(search(solve(hard1)))
    display(search(solve(hard2)))
