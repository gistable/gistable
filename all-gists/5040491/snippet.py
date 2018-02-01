""" Usage: python diff.py FILE1 FILE2

A primitive `diff` in 50 lines of Python.
Explained here: http://pynash.org/2013/02/26/diff-in-50-lines.html
"""

def longest_matching_slice(a, a0, a1, b, b0, b1):
    sa, sb, n = a0, b0, 0

    runs = {}
    for i in range(a0, a1):
        new_runs = {}
        for j in range(b0, b1):
            if a[i] == b[j]:
                k = new_runs[j] = runs.get(j-1, 0) + 1
                if k > n:
                    sa, sb, n = i-k+1, j-k+1, k
        runs = new_runs

    assert a[sa:sa+n] == b[sb:sb+n]
    return sa, sb, n

def matching_slices(a, a0, a1, b, b0, b1):
    sa, sb, n = longest_matching_slice(a, a0, a1, b, b0, b1)
    if n == 0:
        return []
    return (matching_slices(a, a0, sa, b, b0, sb) +
            [(sa, sb, n)] +
            matching_slices(a, sa+n, a1, b, sb+n, b1))

def print_diff(a, b):
    ia = ib = 0
    slices = matching_slices(a, 0, len(a), b, 0, len(b))
    slices.append((len(a), len(b), 0))
    for sa, sb, n in slices:
        for line in a[ia:sa]:
            print "-" + line
        for line in b[ib:sb]:
            print "+" + line
        for line in a[sa:sa+n]:
            print " " + line
        ia = sa + n
        ib = sb + n

if __name__ == '__main__':
    import sys
    def lines(filename):
        with open(filename) as f:
            return [line.rstrip('\n') for line in f.readlines()]
    print_diff(lines(sys.argv[1]), lines(sys.argv[2]))
