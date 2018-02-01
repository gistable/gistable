#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Martine Lenders <mail@martine-lenders.eu>
#
# Distributed under terms of the MIT license.

import csv
import sys

def schulze(C, d):
    res = [[None for i in range(C)] for j in range(C)]
    if len(d) != C:
        raise ValueError("d must be of a dimension equal to C")
    for i in range(C):
        for j in range(C):
            if i == j:
                continue
            if len(d[i]) != C:
                raise ValueError("d[%d] must be of a dimension equal to C" % i)
            if d[i][j] > d[j][i]:
                res[i][j] = int(d[i][j])
            else:
                res[i][j] = 0

    for i in range(C):
        for j in range(C):
            if i == j:
                continue
            for k in range(C):
                if i == k:
                    continue
                if j == k:
                    continue
                res[j][k] = max(res[j][k], min(res[j][i], res[i][k]))

    return res

def read_css(filename, Cs, **fmtparams):
    options = None
    C = len(Cs)
    pref = []
    d = [[0 for i in range(C)] for j in range(C)]
    if C == 0:
        raise ValueError("Expect at least one candidate")
    with open(filename) as csvfile:
        firstline = True
        has_header = csv.Sniffer().has_header(csvfile.read(1024))
        csvfile.seek(0)
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        reader = csv.reader(csvfile, dialect, **fmtparams)
        for row in reader:
            if has_header and firstline:
                options = [row[i] for i in Cs]
                firstline = False
                continue
            pref.append([row[i] for i in Cs])
    if options != None:
        Cs = options
    for p in pref:
        for i in range(C):
            for j in range(C):
                if int(p[i]) < int(p[j]):
                    d[i][j] += 1
    return C, Cs, d

if __name__ == "__main__":
    C, Cs, d = read_css(sys.argv[1], [int(a[0]) for a in sys.argv[2:]])
    res = schulze(C, d)
    winner = [True for _ in Cs]
    for i in range(C):
        for j in range(C):
            if i != j and res[j][i] > res[i][j]:
                winner[i] = False
    for i in range(C):
        if winner[i]:
            print(Cs[i])