#!/usr/bin/env python

# the contents of this file are in the public domain

import os
import random
import sys

def main(args):
    filename = args[0]
    dirname = args[1]
    count = int(args[2])
    with open(filename, 'rb') as f:
        contents = f.read()
    for i in xrange(0, count):
        write_out_with_glitch(contents, os.path.join(dirname, "glitch%02d.jpg" % i))


def write_out_with_glitch(contents, filename):
    size = len(contents)
    print "writing %s bytes to %s..." % (size, filename)
    with open(filename, 'wb') as f:
        for byte in contents:
            if random.randint(0, 999) == 0:
                f.write(chr(random.randint(0, 255)))
            else:
                f.write(byte)


if __name__ == '__main__':
    main(sys.argv[1:])
