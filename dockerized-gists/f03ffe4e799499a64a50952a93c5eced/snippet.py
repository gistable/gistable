""" The problem description:

Given a Data Structure having first n integers and next n chars.
A = i1 i2 i3 ... iN c1 c2 c3 ... cN.Write an in-place algorithm
to rearrange the elements of the array ass A = i1 c1 i2 c2 ... in cn

"""


def swap(arr, ind1, ind2):
    tmp = arr[ind1]
    arr[ind1] = arr[ind2]
    arr[ind2] = tmp


def cycle_decomp(perm):
    lp = len(perm)
    cycles = []
    was = set()
    i = 0

    while len(was) < lp:
        while i in was:
            i += 1

        was.add(i)
        cycle = [i]

        while perm[cycle[-1]] not in was:
            was.add(perm[cycle[-1]])
            cycle.append(perm[cycle[-1]])
        cycles.append(cycle)
    return cycles


def apply_perm(arr, perm):
    cycles = cycle_decomp(perm)

    for cycle in cycles:
        lc = len(cycle)
        if lc == 1:
            continue

        for i in xrange(1, lc):
            swap(arr, cycle[0], cycle[i])


def solve(arr):
    l = len(arr)
    assert l % 2 == 0
    n = l / 2

    move = [None for _ in xrange(l)]

    for i in xrange(n):
        move[i] = 2 * i

    for i in xrange(n, l):
        move[i] = (i % n) * 2 + 1

    apply_perm(arr, move)


if __name__ == "__main__":
    from sys import argv
    n = int(argv[1])
    assert n < 27, "We only have 26 letters in the English alphabet"
    letters = map(chr, xrange(97, 123))
    numbers = range(26)
    arr = numbers[:n] + letters[:n]
    print "before: %s" % (arr,)
    solve(arr)
    print "after: %s" % (arr,)
