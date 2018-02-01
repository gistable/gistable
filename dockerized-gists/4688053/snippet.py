#!/usr/bin/python

"""
Playing around with slightly various ways to simulate uniq in Python.
The different strategies are timed.
Only m0() and m1() do not change the order of the data.
`in` is the input file, `out*` are output files.
"""

infile = 'in'  # Change filename to suit your needs.

def m1():
    s = set()
    with open('out1', 'w') as out:
        for line in open(infile):
            if line not in s:
                out.write(line)
                s.add(line)

def m2():
    s = set()
    out = open('out2', 'w')
    for line in open(infile):
        if line not in s:
            out.write(line)
            s.add(line)
    out.close()

def m3():
    s = set()
    for line in open(infile):
        s.add(line)
    out = open('out3', 'w')
    for line in s:
        out.write(line)
    out.close()

def m4():
    s = set()
    for line in open(infile):
        s.add(line)
    out = open('out4', 'w').writelines(s)

def m5():
    uniqlines = set(open(infile).readlines())
    out = open('out5', 'w').writelines(uniqlines)

if __name__ == '__main__':
    import timeit
    print 'm1', timeit.timeit('m1()', setup='from __main__ import m1', number=1000)
    print 'm2', timeit.timeit('m2()', setup='from __main__ import m2', number=1000)
    print 'm3', timeit.timeit('m3()', setup='from __main__ import m3', number=1000)
    print 'm4', timeit.timeit('m4()', setup='from __main__ import m4', number=1000)
    print 'm5', timeit.timeit('m5()', setup='from __main__ import m5', number=1000)