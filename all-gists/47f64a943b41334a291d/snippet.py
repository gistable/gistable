#!/usr/bin/env python
import os
import sys


def main(argv):
    fname = ""

    if len(argv) > 0:
        fname = argv[0]

    if not os.path.exists(fname) and not os.path.isfile(fname):
        print "expecting file!"
        return

    if not fname.endswith('.img'):
        print "expection img file"
        return

    raw_name = fname + ".raw"
    extract_name = fname + ".dir"

    strip_cmd = 'dd if="%s" bs=1 skip=64 of="%s"' % (fname, raw_name)
    print strip_cmd
    os.system(strip_cmd)
    extract_cmd = 'unsquashfs -d "%s" "%s"' % (extract_name, raw_name)
    print extract_cmd
    os.system(extract_cmd)
    print "done"

if __name__ == "__main__":
    main(sys.argv[1:])