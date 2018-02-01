import numpy

MODEL = """\
53..7....
6..195...
.98....6.
8...6...3
4..8.3..1
7...2...6
.6....28.
...419..5
....8..79
"""

def select(list):
    return ' '.join('(select a {0})'.format(l) for l in list)

def main(model):
    lines = []
    lines.append('(set-logic AUFLIRA)')
    lines.append('(set-option :produce-models true)')
    lines.append('(declare-fun a () (Array Int Int))')
    
    index = numpy.arange(81).reshape(9,9)
    for i in xrange(9):
        lines.append('(assert (distinct {}))'.format(select(index[:,i])))
        lines.append('(assert (distinct {}))'.format(select(index[i,:])))

        r0 = (i % 3) * 3
        c0 = (i // 3) * 3
        lines.append('(assert (distinct {}))'.format(
            select(index[r0:r0+3,c0:c0+3].ravel())
        ))

    for i in xrange(81):
        lines.append('(assert (< 0 (select a {0})))'.format(i))
        lines.append('(assert (> 10 (select a {0})))'.format(i))

    for i, n in zip(xrange(81), model):
        if n != '.':
            lines.append('(assert (= {0} (select a {1})))'.format(n, i))

    lines.append('(check-sat)')
    lines.append('(get-value ({}))'.format(select(xrange(81))))

    return lines

with open('sod1.smt', 'w') as out:
    model = MODEL.replace('\n', '').replace('\r', '').strip()
    out.write('\n'.join(main(model)))
    out.write('\n')
    print "Done, now run 'builds/bin/cvc4  --lang smt sod1.smt'"
