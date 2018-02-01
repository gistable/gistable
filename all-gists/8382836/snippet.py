#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

def main():
    with open('DRAKS0005.sl2', 'rb') as fo:
        fo.seek(0x2c0, 0)
        for slot in range(0, 10):
            fo.seek(0x100, 1)
            name = fo.read(32)
            if name[0] != '\00':
                fo.seek(-0x120, 1)
                fo.seek(0x1f128, 1)
                deaths = fo.read(4)
                fo.seek(-0x04, 1)
                fo.seek(-0x1f128, 1)
                print "name: %s\tdeaths: %d" % (name.decode('utf-16').split('\00')[0], struct.unpack('i', deaths)[0])
            else:
                fo.seek(-0x120, 1)

            fo.seek(0x60190, 1)
    raw_input("Press Enter to continue...")

if __name__ == '__main__':
    main()