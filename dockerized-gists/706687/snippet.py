'''Parens
Enumerate nested parenthesis.

Implements Algorithm P from Knuth's the Art of Computer Programming v. 4
directly with minimal optimizations for python.

Usage: python parens.py number
'''
import sys

def printKParens(k):
    ''' Prints all sets of nested parenthesis of order k'''
    n = k # number of parens to place
    
    if n == 1: print "()"  # trivial case, Algorithm P requires n >= 2
    if n <= 1: return
    
    # P1 Initialize
    # strings are immutable in python, so this uses a list
    # initialize parenthesis next to each other with a pad at a[0]
    # serving as a stop signal for the inner loop
    # the 'string' we want is really a[1:2n+1]
    # e.g. )()()() 
    a = range(2*n + 1)
    a[0] =")"
    for k in range(1, n + 1):
        a[2*k - 1] = "("
        a[2*k] = ")"    
    
    m = 2*n - 1 # index value

    while True:
        # P2 visit step
        print "".join(a[1:])
        # P3 easy case
        a[m] = ")"
        if a[m - 1] == ")":
            a[m - 1] = "("
            m = m - 1
        else:
            # P4 find j
            j = m - 1
            k = 2*n - 1
            while a[j] == "(": # almost always short
                a[j] = ")"
                a[k] = "("
                j = j - 1
                k = k - 2
            # P5 increase a_j
            if j == 0:
                return
            else:
                a[j] = "("
                m = 2*n - 1

if __name__ == '__main__':
    try:
        print "Generating all trees of " + sys.argv[1] + " nested parens."
    except IndexError:
        print __doc__
        sys.exit(1)
    
    printKParens(int(sys.argv[1]))