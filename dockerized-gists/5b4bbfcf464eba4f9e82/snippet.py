#! /usr/bin/env python


def printmatrix(matrix):
    """ source:
    http://stackoverflow.com/questions/13214809/pretty-print-2d-python-list """
    s = [[str(e) for e in row] for row in [['['+str(n)+']' for n in range(1, 7)]]+matrix]
    lens = [len(max(col, key=len)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = ['['+str(n)+"]\t"+fmt.format(*row) for (row, n) in zip(s, range(0, len(s)+1))]
    table[0] = '   '+table[0][3:]  # to remove the [0]
    print('\n'.join(table))

one = [[0]*6 for x in range(6)]  # (w, l) are the chances of wining / losing 1
two = [[0]*6 for x in range(6)]  # (w, d, l) are the chances of winning 2 / 1v1 / losing 2
exp = [[0]*6 for x in range(6)]  # (e1, e2) are the expected values throwing 1 or 2 dice respectively
choice = [[0]*6 for x in range(6)]  # best choice based on expected value

for a in range(0, 6):
    for b in range(0, 6):
        if (a < b):
            a, b = b, a
        one[a][b] = ((6-a)/6.0, 1 - (6-a)/6.0)
        two[a][b] = [0, 0, 0]
        for c in range(1, 7):
            for d in range(1, 7):
                if c < d:
                    c, d = d, c
                if c >= a + 1:
                    if d >= b + 1:
                        two[a][b][0] += 1
                    else:
                        two[a][b][1] += 1
                else:
                    if d >= b + 1:
                        two[a][b][1] += 1
                    else:
                        two[a][b][2] += 1
        two[a][b] = tuple([x/36.0 for x in two[a][b]])
        exp[a][b] = (one[a][b][0] - one[a][b][1], 2*two[a][b][0] - 2*two[a][b][2])
        choice[a][b] = '1' if exp[a][b][0] > exp[a][b][1] else '2'

for a in range(1, 6):
    for b in range(0, a):
        one[b][a] = one[a][b]
        two[b][a] = two[a][b]
        exp[b][a] = exp[a][b]
        choice[b][a] = choice[a][b]

for a in range(0, 6):
    for b in range(0, 6):
        one[a][b] = "{0:.2f} {1:.2f}".format(*one[a][b])
        two[a][b] = "{0:.2f} {1:.2f} {2:.2f}".format(*two[a][b])
        exp[a][b] = "{0:.2f} {1:.2f}".format(*exp[a][b])

print(">>>> One die (w/l):")
printmatrix(one)
print(">>>> Two dice (w2/1v1/l2):")
printmatrix(two)
print(">>>> Expected values (1 die, 2 dice):")
printmatrix(exp)
print(">>>> Best choice:")
printmatrix(choice)
