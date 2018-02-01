"""Usage: python matchcolors.py good.jpg bad.jpg save-corrected-as.jpg"""

from scipy.misc import imread, imsave
from scipy import mean, interp, ravel, array
from itertools import izip
import sys

def mkcurve(chan1,chan2):
    "Calculate channel curve by averaging target values."
    fst = lambda p: p[0]
    snd = lambda p: p[1]
    sums = {}
    for v1, v2 in izip(ravel(chan1), ravel(chan2)):
        old = sums.get(v1, [])
        sums.update({v1: old + [v2]})
    c = array( [ (src,mean(vals))
                 for src,vals in sorted(sums.iteritems()) ])
    nvals = interp(range(256), c[:,0], c[:,1], 0, 255)
    return dict(zip(range(256), nvals))

def correct_bad(good, bad):
    "Match colors of the bad image to good image."
    r, g, b = bad.transpose((2,0,1))
    r2, g2, b2 = good.transpose((2,0,1))
    rc = mkcurve(r,r2)
    gc = mkcurve(g,g2)
    bc = mkcurve(b,b2)
    corr = bad.copy()
    h, w = corr.shape[:2]
    for row in xrange(h):
        for col in xrange(w):
            r,g,b = corr[row,col]
            corr[row,col] = [rc[r], gc[g], bc[b]]
    return corr

if __name__ == "__main__":
    good, bad, saveas = sys.argv[1:1+3]
    good = imread(good)
    bad = imread(bad)
    assert(good.shape == bad.shape)
    corrected = correct_bad(good,bad)
    imsave(saveas, corrected)
