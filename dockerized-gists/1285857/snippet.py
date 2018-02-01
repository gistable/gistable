#!/usr/bin/python
# Prints some simple information about ucode firmwares
# such as those used by Intel Wifi cards
# 
# Version 1.0 Jan 2011
# by Andrew Brampton
#
# Example
#   ./ucode.py /lib/firmware/*.ucode
#

import sys
from struct import unpack

def main(files):
        width = 0
        for filename in files:
                if len(filename) > width: width = len(filename) + 1

        for filename in files:
                try:
                        f = open(filename, 'rb')
                except IOError:
                        continue;

                header = f.read(4)

                print "%s:" % filename.ljust(width),

                # New firmeware have zeros, magic, readable, version
                if header == '\0\0\0\0':
                        magic    = f.read(4)
                        if magic != 'IWL\n':
                                print 'Invalid ucode file'
                                continue;
                        readable = ' (' + f.read(64).strip("\n\0") + ')'
                        header   = f.read(4)
                else:
                        readable = ''

                serial, api, minor, major = unpack('BBBB', header)
                print ("ver %u.%u.%u.%u%s") % (major, minor, api, serial, readable)

if __name__ == "__main__":
        if len(sys.argv) <= 1:
                print 'Displays information about ucode firmware, such as those used by Intel found in /lib/firmware'
                print 'Usage: ucode.py  ...'
        main(sys.argv[1:])