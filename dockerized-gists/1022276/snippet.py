# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""Usage: ./fizzbuzz.py <filename>"""


def fizzbuzz(f, b, l):
    return [(i % f == 0 and 1 or 0) * 'F' \
            + (i % b == 0 and 1 or 0) * 'B' \
            or '%d' % i \
            for i in range(1, l + 1)]

if __name__ == '__main__':
    import sys
    if len(sys.argv) <= 1:
        sys.exit(__doc__)

    dat = None
    try:
        dat = open(sys.argv[1])
        for l in dat.readlines():
            f, b, l = l.split(' ')
            print ' '.join(fizzbuzz(int(f), int(b), int(l)))
    except Exception, e:
        sys.exit(e)
    finally:
        if dat:
            dat.close()