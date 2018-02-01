#!/usr/bin/env python2

import argparse
import json
import os
import string
import sys
import zlib

def dump(data, desc = None):
    dlen = len(data)

    if desc:
        sys.stdout.write("%s:%s" % (desc, os.linesep))

    i = 0

    while i < dlen:
        sys.stdout.write("  %08x  " % (i))

        for j in range(16):
            if (i + j) < dlen:
                c = ord(data[i + j])
                sys.stdout.write("%02x " % (c))
            else:
                sys.stdout.write("   ")

            if j == 7:
                sys.stdout.write(" ")

        sys.stdout.write(" |")

        for j in range(16):
            if (i + j) >= dlen:
                break

            c = data[i + j]

            if not c in string.printable or c.isspace():
                c = "."

            sys.stdout.write(c)

        sys.stdout.write("|%s" % (os.linesep))
        i += 16

    sys.stdout.write("  %08x%s" % (i, os.linesep))

def zdump(data):
    dlen = len(data)
    s    = 0

    while True:
        if s >= dlen:
            return

        s = data.find(chr(0x78), s + 1)

        if (s < 0) or ((s + 1) >= dlen):
            return

        try:
            zata = zlib.decompress(data[s:])
        except:
            return

        try:
            js = json.loads(zata)
            js = json.dumps(js, indent = 4)

            sys.stdout.write("Decompressed:%s" % (os.linesep))

            for l in js.splitlines():
                sys.stdout.write("  %s%s" % (l, os.linesep));
        except:
            dump(zata, "Decompressed")
        finally:
            break

def dissect(data):
    dlen = len(data)
    i    = 0

    while i < dlen:
        byte = ord(data[i])
        s  = i
        i += 1

        pype  = (byte & 0xF0) >> 4
        plags = byte & 0x0F

        size = 0
        mult = 1

        while True:
            byte = ord(data[i])
            i += 1

            size += (byte & 127) * mult;
            mult *= 128

            if (byte & 128) == 0:
                break

        i += size
        dump(data[s:i], "Packet %d (flags: 0x%0X)" % (pype, plags))
        zdump(data[s:i])
        sys.stdout.write(os.linesep)

def parseargs():
    parser = argparse.ArgumentParser(
        description = "MQTT data dumper"
    )

    parser.add_argument(
        type    = str,
        action  = "store",
        dest    = "dumpfile",
        metavar = "PATH",
        help    = "specify the dump file"
    )

    return parser.parse_args()

def main():
    args = parseargs()
    fp   = open(args.dumpfile, "rb")
    data = fp.read()

    dissect(data)
    fp.close()

if __name__ == "__main__":
    main()
