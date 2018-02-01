#!/usr/bin/env python

import bz2
import datetime
import os
import sys
import time
import urllib2
import warnings

badclients = (
    'FDM 3.x',
    'pep381client/1.5',
    'warehouse/0.1dev1',
    'z3c.pypimirror/1.0.15.1',
    'z3c.pypimirror/1.0.16',
    'z3c.pypimirror/1.0.16.1',
    'z3c.pypimirror/1.0.16.2',
)

def filenames():
    date = datetime.date.today()
    while True:
        date -= datetime.timedelta(1)
        yield time.strftime('%Y-%m-%d', date.timetuple())

def statsfiles(cachedir='.'):
    baseurl = 'http://pypi.python.org/stats/days/%s.bz2'
    for basename in filenames():
        fname = os.path.join(cachedir, basename)
        try:
            yield open(fname, 'r')
        except IOError:
            print >>sys.stderr, 'Fetching %s...' % (baseurl % basename),
            sys.stderr.flush()
            r = urllib2.urlopen(baseurl % basename)
            print >>sys.stderr, 'done.'
            content = bz2.decompress(r.read())
            with open(fname, 'w') as f:
                f.write(content)
            yield open(fname, 'r')

def statistics(package, cachedir='.', ignore_clients=[], mindays=0):
    stats = {}
    for f in statsfiles(cachedir=cachedir):
        n = 0
        for line in f:
            if line.startswith('%s,' % package):
                p, dl, client, downloads = line.split(',')
                if client not in ignore_clients:
                    n += int(downloads)
        f.close()
        mindays -= 1
        if n > 0:
            stats[os.path.basename(f.name)] = n
        elif mindays < 1:
            return stats

def gnuplot(package, stats=None, outfile=None, script="""\
    set xdata time
    set ydata
    set timefmt "%%Y-%%m-%%d"
    set format x "%%m/%%d"
    
    set xlabel "date"
    set ylabel "# of downloads"
    set title "Popularity of PyPI package %(package)s"
    set x2label "%(total)d downloads total"

    set xrange ["%(xrange_min)s":"%(xrange_max)s"]
    set yrange [0:*]
    
    set terminal png
    set output "%(outfile)s"
    
    plot "%(datfile)s" using 1:2 with lines title ""
"""):
    if outfile is None:
        outfile = package + '.png'

    if stats is None:
        stats = statistics(package)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        datfile = os.tmpnam()
        scriptfile = os.tmpnam()

    script %= {'package': package,
               'xrange_min': min(stats), 'xrange_max': max(stats),
               'outfile': outfile, 'datfile': datfile,
               'total': sum(stats.values())}

    try:
        with open(datfile, 'w') as f:
            for key in sorted(stats):
                f.write('%s %d\n' % (key, stats[key]))

        with open(scriptfile, 'w') as f:
            f.write(script)

        os.system('gnuplot %s' % scriptfile)
    finally:
        os.unlink(datfile)
        os.unlink(scriptfile)

if __name__ == '__main__':
    for package in sys.argv[1:]:
        print "Package", package        

        stats = statistics(package)
        gnuplot(package, stats)
        print "Total downloads:", sum(stats.values())

        stats = statistics(package, ignore_clients=badclients, mindays=len(stats))
        gnuplot(package, stats, outfile='%s.filtered.png' % package)
        print "Total downloads (actual):", sum(stats.values())

        print
