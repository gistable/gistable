#!/usr/bin/env python3
# -*- mode: python -*-

# This program is free software. It comes without any warranty, to the extent
# permitted by applicable law. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License, Version 2, as
# published by Sam Hocevar. See http://sam.zoy.org/wtfpl/COPYING for more
# details.

# Some useful resources:
# - http://atomicparsley.sourceforge.net/mpeg-4files.html
# - http://developer.apple.com/library/mac/#documentation/QuickTime/QTFF/QTFFChap2/qtff2.html
# - http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/QuickTime.html

import datetime
from optparse import OptionParser
import os.path
import struct
import sys
import time

CONTAINER_ATOMS = ["moov", "trak", "mdia"]
# Also containers (but not interesting): "minf", "dinf", "stbl"

_ATOMS = {
    "pnot": (12, "I2x4s2x",
             ("Modification time", "Atom type"),
             (0,)),
    "mvhd": (100, "4x2I88x",
             ("Creation time", "Modification time"),
             (4, 8)),
    "tkhd": (84, "4x2I72x",
             ("Creation time", "Modification time"),
             (4, 8)),
    "mdhd": (24, "4x2I12x",
             ("Creation time", "Modification time"),
             (4, 8)),
}

_DATES = ("Creation time", "Modification time")

class Mov(object):
    def __init__(self, fn):
        self._fn = fn
        self._offsets = []

    def parse(self):
        fsize = os.path.getsize(self._fn)
        print("File: {} ({} bytes, {} MB)".format(self._fn, fsize, fsize / (1024.**2)))
        with open(self._fn, "rb") as self._f:
            self._parse(fsize)

    def _parse(self, length, depth=0):
        prefix = "  "*depth + "- "
        n = 0
        while n < length:
            data = self._f.read(8)
            #print(len(data), data)
            al, an = struct.unpack(">I4s", data)
            an = an.decode()
            print("{}Atom: {} ({} bytes)".format(prefix, an, al))

            if an in _ATOMS:
                self._parse_atom(an, al-8, depth)
            elif an == "udta":
                self._parse_udta(al-8, depth)
            elif an == "ftyp":
                self._read_ftyp(al-8, depth)
            elif an in CONTAINER_ATOMS:
                self._parse(al-8, depth+1)
            else:
                self._f.read(al-8)
            n += al

    def _parse_atom(self, atom, length, depth):
        spec = _ATOMS[atom]
        assert length == spec[0]
        pos = self._f.tell()
        prefix = "  "*depth + "  | "
        v = struct.unpack(">"+spec[1], self._f.read(length))
        k = spec[2]
        for i in range(len(k)):
            vv = v[i]
            if type(vv) == bytes:
                vv = vv.decode()
            elif k[i] in _DATES:
                vv = self._macdate2date(vv)
            print("{}{}: {}".format(prefix, k[i], vv))
        for offset in spec[3]:
            self._offsets.append(pos + offset)

    def _read_ftyp(self, length, depth):
        prefix = "  "*depth + "  | "
        data = self._f.read(8)
        brand, version = struct.unpack(">4sI", data)
        brand = brand.decode("latin1")
        print("{}Brand: {}, version: {}".format(prefix, brand, version))
        self._f.read(length-8)

    def _parse_udta(self, length, depth):
        prefix = "  "*depth + "  | "
        n = 0
        while n < length:
            atom_size, data_type = struct.unpack(">I4s", self._f.read(8))
            data_type = data_type.decode("latin1")
            raw = self._f.read(atom_size-8)
            if data_type[0] == "©":
                print("{}{}: {}".format(prefix, data_type, raw[3:].decode()))
            else:
                print("{}{} ({} bytes)".format(prefix, data_type, atom_size-8))
            n += atom_size

    def _macdate2date(self, md):
        d = datetime.datetime(1904, 1, 1) + datetime.timedelta(seconds=md)
        return "{} ({})".format(d, md)

    def _date2macdate(self, d):
        td = datetime.datetime(1970, 1, 1) - datetime.datetime(1904, 1, 1)
        dd = d + td
        sec = time.mktime(dd.timetuple()) - time.timezone
        return int(sec)

    def set_date(self, d):
        md = self._date2macdate(d)
        print("New date: {} ({})".format(d, md))
        with open(self._fn, "r+b") as f:
            print("Writing new date at {} positions...".format(len(self._offsets)))
            for offset in self._offsets:
                f.seek(offset)
                data = struct.pack(">I", md)
                f.write(data)
            f.flush()
            print("Touching file...")
            ts = time.mktime(d.timetuple())
            os.utime(self._fn, (ts, ts))
        print("Done! :)")

if __name__ == "__main__":
    usage = "Usage: %prog [options] file.mov [\"YYYY-MM-DD hh:mm:ss\"]"
    parser = OptionParser(usage)
    
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.error("incorrect number of arguments")
        
    m = Mov(args[0])
    m.parse()

    if len(args) > 1:
        d = datetime.datetime.strptime(args[1], "%Y-%m-%d %H:%M:%S")
        m.set_date(d)
