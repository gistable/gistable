#!/usr/bin/env python3
# -*- coding: ascii -*-

# Basic backtracking Sudoku solver.

SET1T9 = frozenset(range(1, 10))
SINGLETONS = tuple(frozenset((i,)) for i in range(10))

# Return the indices of the same row/column/section as the given base index.
# Without the second argument, returns the union of all those *without* the
# base index (this is the set actually used for something).
def indices(base, dir=None):
    y, x = divmod(base, 9)
    if dir == 'r':
        b = y * 9
        return frozenset(range(b, b + 9))
    elif dir == 'c':
        return frozenset(i * 9 + x for i in range(9))
    elif dir == 's':
        bx, by = x // 3 * 3, y // 3 * 3
        return frozenset(i * 9 + j for i in range(by, by + 3)
                         for j in range(bx, bx + 3))
    else:
        return (indices(base, 'r') | indices(base, 'c') |
                indices(base, 's')).difference((base,))

# Actually solve the Sudoku.
# Input is a flat row-major 81-entry list.
def solve(inpt):
    # Set value in output and cascade effect to all now-certain cells.
    def update(output, possibilities, index, value=None):
        if value is None:
            # HACK: Using iterable unpacking to retrieve the value.
            (value,) = possibilities[index]
        output[index] = value
        for i in indices(index):
            possibilities[i] -= SINGLETONS[value]
            if not possibilities[i]:
                return False
            elif len(possibilities[i]) == 1 and not output[i]:
                if not update(output, possibilities, i): return False
        return True
    # Apply backtracking to find a solution.
    def backtrack(output, possibilities, sn=0):
        # Find an empty cell.
        for n, i in enumerate(output[sn:], sn):
            if i: continue
            # Try all possibilities.
            for v in possibilities[n]:
                # Clone state.
                out, poss = list(output), list(possibilities)
                # Try value.
                if not update(out, poss, n, v): continue
                # Good, next one.
                res = backtrack(out, poss, n + 1)
                if res: return res
            return None
        # No empty cells left; done.
        return output
    # General setup.
    output = [None] * 81
    possibilities = [SET1T9 for _ in range(81)]
    # Read input.
    for n, i in enumerate(inpt):
        if not i: continue
        if not update(output, possibilities, n, i): return None
    # Run the main part
    return backtrack(output, possibilities)

# Verify that the given Sudoku is valid.
def validate(data):
    assert len(data) == 81, "Bad length"
    for n, i in enumerate(data):
        assert not i or i in SET1T9, "Bad value at #%s" % n
        others = frozenset(filter(None, (data[j] for j in indices(n))))
        assert i not in others, "Value at #%s is repeated" % n
    return all(data)

# Render a string representation of the Sudoku.
def format_sudoku(data):
    ret = []
    for n, i in enumerate(data):
        ret.append(' ' if n else '[')
        ret.append(str(i) if i else '.')
        ret.append(']' if n == 80 else '\n' if n % 9 == 8 else '')
    return ''.join(ret)

# Main function.
SUDOKU1 = (0, 0, 1, 0, 0, 0, 2, 0, 0,
           0, 3, 0, 0, 0, 0, 0, 4, 0,
           5, 0, 0, 0, 3, 0, 0, 0, 6,
           0, 0, 0, 1, 0, 7, 0, 0, 0,
           0, 4, 0, 0, 0, 0, 0, 8, 0,
           0, 0, 0, 9, 0, 2, 0, 0, 0,
           3, 0, 0, 0, 0, 0, 0, 0, 8,
           0, 6, 0, 0, 5, 0, 0, 3, 0,
           0, 0, 2, 0, 0, 0, 7, 0, 0)
def main():
    sudoku = SUDOKU1
    validate(sudoku)
    print (format_sudoku(sudoku))
    print ('->')
    res = solve(sudoku)
    if res: validate(res)
    print (format_sudoku(res) if res else 'None')

if __name__ == '__main__': main()
