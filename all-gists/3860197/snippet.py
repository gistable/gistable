#!/usr/bin/env python

"""Usage:
    python plot_pr_curve.py
"""

import sys
import numpy as np
import pylab as pl
from sklearn.metrics import precision_recall_curve

def read(fname):
    y_test = []
    probas = []
    with open(fname, 'r') as f:
        for line in f:
            cols = line.strip().split()

            if not (len(cols) == 4 or len(cols) == 5): continue
            if not cols[0].isdigit(): continue

            y_test.append( float(cols[1].split(':')[-1]) )

            proba = float(cols[-1].split(',')[-1].replace('*', ''))
            probas.append(proba)
    return np.array(y_test), np.array(probas)

def plot_precision_recall(lines, fname):
    pl.clf()

    for precision, recall, label in lines:
        pl.plot(recall, precision, label=label)
    pl.xlabel('Recall')
    pl.ylabel('Precision')
    pl.ylim([0.0, 1.05])
    pl.xlim([0.0, 1.0])
    pl.title('Precision-Recall')
    pl.legend(loc="upper right")
    pl.savefig(fname)

def main(fnames):
    lines = []

    for fname, label in fnames:
        y_test, probas = read(fname)
        precision, recall, threshold = precision_recall_curve(y_test, probas)

        lines.append( (precision, recall, label) )
    png_fname = 'pr_curve.png'
    plot_precision_recall(lines, png_fname)

if __name__ == '__main__':
    fnames = (
        ('file1.txt', 'with feature sets A,B,C'),
        ('file2.txt', 'with feature setes B, C, D'),
        ('file3.txt', 'with feature setes F, G, H'),
        ('file4.txt', 'with feature setes B, C, D'),
        ('file5.txt', 'with feature setes B, C, D'),
    )

    main(fnames)
