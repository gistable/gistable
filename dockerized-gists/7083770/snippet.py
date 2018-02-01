#!/usr/bin/env python3
# encoding: utf-8

# Public domain.
# 2013, Pyry Jahkola.

from __future__ import print_function
import sys, time

def progress(iterable, n=None, **kwargs):
    """\
    progress(iterable[, n][, file=sys.stderr, interval=...])

    Iterate over `iterable` (of estimated length `n`), printing progress display
    to `file`. Set the keyword argument `take` to limit maximum iterations.

    Output like ' 93% ETA:  00:01:24' is printed every completed percent or
    every `interval` seconds, and '100% Time: 00:13:29.123' at the end. If n is
    not given and len(iterable) not defined, there will be no ETA but a time
    elapsed instead.
    """
    # TODO: let the user choose to show the last iterated value instead of
    #       iteration number in the indeterminate display, e.g. when generating
    #       primes
    if not n and hasattr(iterable, '__len__'): n = len(iterable)
    file = kwargs.get('file', sys.stderr)
    interval = kwargs.get('interval', 0.5 if n is None else 1)
    it, t0, elapsed = iter(iterable), time.time(), (lambda: time.time() - t0)
    write = lambda msg: sys.stdout.flush() or file.write(msg) or file.flush()
    hms   = lambda sec: '{:02}:{:02}:{:02}'.format(*divmods(int(sec), 60, 60))
    hmsm  = lambda sec: '{:02}:{:02}:{:02}.{:03}'.format(
                                        *divmods(int(1000 * sec), 60, 60, 1000))
    def update_percentage(i, percentage, previous_time):
        x, i, t = next(it), (i + 1), elapsed()
        p = 100 * i // n
        if p == percentage and t < previous_time + interval:
            return x, (i, percentage, previous_time)
        write('\r{:3}% - ETA: {}\r'.format(p, hms(max(n * t / i - t + 0.5, 0))))
        return x, (i, p, t)
    def update_elapsed(i, _, previous_time):
        x, i, t = next(it), (i + 1), elapsed()
        if t < previous_time + interval: return x, (i, 100, previous_time)
        write('\r{:6} - Elapsed: {}\r'.format(i, hms(t)))
        return x, (i, 100, t)
    def finish(i, *_):
        write('\r{:6} - Time: {}\n'.format(i, hmsm(elapsed())))
    def generate(*state):
        try:
            while state[1] < 100:
                x, state = update_percentage(*state)
                yield x
            while True:
                x, state = update_elapsed(*state)
                yield x
        except StopIteration:
            finish(*state)
            raise
    return generate(0, 0 if n else 100, -1) # iteration, percentage, prev_time

def divmods(p, *qs):
    """\
    Split number p to an odd basis defined by radices qs from biggest to lowest:
        divmods(p, q1, q2) -> (p // q2 // q1, p // q2 % q1, p % q2)

    E.g. To turn seconds into a tuple of days, hours, minutes and seconds, the
    radices would be 24 (hrs/day), 60 (mins/hour), and 60 (secs/min):

        >>> divmods(((364*24+23)*60+58)*60+59, 24, 60, 60)
        (364, 23, 58, 59)
    """
    rs = []
    for q in reversed(qs):
        p, r = divmod(p, q)
        rs.append(r)
    rs.append(p)
    rs.reverse()
    return tuple(rs)

def filesize(file):
    if isinstance(file, str):
        with open(file) as f: return filesize(f)
    initial_pos = file.tell()
    buf_size = 1024 * 1024
    read_f = file.read # loop optimization
    buf = read_f(buf_size)
    if not buf:
        return 0 # Empty file
    lines = 1
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)
    file.seek(initial_pos)
    return lines

def progresslines(file, *a, **kw):
    "Print progress information when iterating over lines of file."
    print('Estimating size...', end='\r', file=sys.stderr)
    f = open(file, *a, **kw)
    return progress(f, filesize(f))
