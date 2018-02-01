#!/usr/bin/env python

from __future__ import with_statement

class It:
    def __init__(self, s):
        ''' make a new test '''
        self.s = s
        self.status = None
    
    def __enter__(self, *stuff):
        ''' return self for use in with statement '''
        return self
    
    def __exit__(self, type, value, traceback):
        ''' print test status '''
        if self.status:
            print 'PASS:',
        else:
            print 'FAIL:',
        print self.s
    
    def should_be_equal(self, a, b):
        self.status = (a == b)
    
    def should_not_be_equal(self, a, b):
        self.status = (a != b)


with It('passes') as test:
    test.should_be_equal(1, 1)

with It('also passes') as test:
    test.should_not_be_equal(0, 1)

with It('does not pass') as test:
    test.should_be_equal(0, 1)

with It('also does not pass') as test:
    test.should_not_be_equal(0, 0)