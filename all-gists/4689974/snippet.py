#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Table(object):

    def __init__(self, table):

        self.row_len = len(table)
        self.col_len = len(table[0])
        self.table = table

    def row(self, n):
        return self.table[n]

    def col(self, n):
        return [self.table[i][n] for i in xrange(self.row_len)]

class FlatTable(object):

    def __init__(self, table):

        self.row_len = len(table)
        self.col_len = len(table[0])

        self.elemets = []
        for row in table:
            self.elemets.extend(row)


    def row(self, n):
        start = self.col_len*n
        return self.elemets[start:start+self.col_len]

    def col(self, n):
        return self.elemets[n::self.col_len]

def dump(table):

    for i in xrange(table.row_len):
        print table.row(i)
    print

    for j in xrange(table.col_len):
        print table.col(j)
    print

def test_row(table):
    for i in xrange(table.row_len):
        table.row(i)

def test_col(table):
    for j in xrange(table.col_len):
        table.col(j)

if __name__ == '__main__':

    t = [[ 1,  2,  3,  4],
         [ 5,  6,  7,  8],
         [ 9, 10, 11, 12],
         [13, 14, 15, 16]]

    from timeit import timeit

    table = Table(t)

    print "# Table's Dump:"
    dump(table)

    print "# Table's Row Test:"
    r = timeit(lambda: test_row(table))
    print r
    print
    print "# Table's Col Test:"
    c = timeit(lambda: test_col(table))
    print c
    print
    print "# Table's Test:"
    print r+c
    print

    ftable = FlatTable(t)

    print "# FlatTable's Dump:"
    dump(ftable)

    print "# FlatTable's Row Test:"
    r = timeit(lambda: test_row(ftable))
    print r
    print
    print "# FlatTable's Col Test:"
    c = timeit(lambda: test_col(ftable))
    print c
    print
    print "# FlatTable's Test:"
    print r+c
    print