#!/usr/bin/env python
"""
MSN ApplicationId patcher for pidgin/bitlbee/whatever
(because you're too lazy to rebuild the whole thing.)

Usage examples:

    python patch.py /usr/sbin/bitlbee
    python patch.py /usr/lib/purple-2/libmsn.so

It will output the modified file to the current directory.
Backup the original file and replace it with the new version.

If you're lucky, it will work.
If not, don't be lazy and rebuild it.
"""

import os
import sys
import mmap
import shutil

WLM_2008_ID = b"CFE80F9D-180F-4399-82AB-413F33A1FA11"   # blocked
WLM_2009_ID = b"AAD9B99B-58E6-4F23-B975-D9EC1F9EC24A"   # blocked
WLM_2012_ID = b"484AAC02-7F59-41B7-9601-772045DCC569"   # working, may be buggy
SKYPE_ID    = b"F6D2794D-501F-443A-ADBE-8F1490FF30FD"   # working, may be buggy

# "buggy" means you may show up as offline to others - test talking with a contact!

## you can try switching these around!
OLD_ID = WLM_2008_ID
NEW_ID = SKYPE_ID

## examples (remove # from the relevant lines)

## use the WLM 2012 key instead (may work better for you)
#OLD_ID = WLM_2008_ID
#NEW_ID = WLM_2012_ID

## if you want to patch an already patched binary to use 2012 instead of 2009:
#OLD_ID = WLM_2009_ID
#NEW_ID = WLM_2012_ID


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return

    filename = sys.argv[1]
    out_filename = os.path.abspath(os.path.basename(filename) + ".out")

    shutil.copy(filename, out_filename)
    print("Writing to " + out_filename)

    fd = os.open(out_filename, os.O_RDWR | getattr(os, 'O_BINARY', 0))
    map = mmap.mmap(fd, 0, access=mmap.ACCESS_WRITE)

    changes = 0

    offset = map.find(OLD_ID)

    while offset != -1:
        print("Found old ID at offset: %d (0x%x)" % (offset, offset))
        map.seek(offset)
        map.write(NEW_ID)

        changes += 1

        offset = map.find(OLD_ID)

    if not changes:
        print("Not found")
    else:
        print("%s IDs changed" % changes)

if __name__ == '__main__':
    main()
