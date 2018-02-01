#!/usr/bin/env python2

# NOTE: Use of this script is deprecated, instead I recommend you use
#
# $ unzip -LL eui_v1_20.zip -d "$HOME/.steam/steam/SteamApps/common/Sid Meier's Civilization V/steamassets/assets/dlc"
#
# to make use of the unzip command's built-in conversion to lowercase filenames
# (thanks reddit user /u/xkero and github user Mfdas)

import os
import shutil
import sys 
import tempfile
import zipfile

# Verify this is the right path on your system
DLC_DIR = '~/.steam/steam/SteamApps/common/Sid Meier\'s Civilization V/steamassets/assets/dlc'
EUI_DIR = 'UI_bc1'

if __name__ == '__main__':
    # Quick and dirty argument parsing
    if len(sys.argv) != 2:
        print 'Usage: %s [ZIPFILE]' % sys.argv[0]
        sys.exit(-1)

    eui_zipfile = sys.argv[1]

    try:
        tempdir = tempfile.mkdtemp()
        with zipfile.ZipFile(sys.argv[1], 'r') as zf: 
            zf.extractall(tempdir)

        srcdir = os.path.join(tempdir, EUI_DIR)
        dstdir = os.path.join(os.path.expanduser(DLC_DIR), EUI_DIR.lower())
        shutil.copytree(srcdir, dstdir)

        os.chdir(dstdir)
        for root, dirnames, filenames in os.walk('.', topdown=False):
            for filename in dirnames + filenames:
                orig = os.path.join(root, filename)
                new = orig.lower()
                try:
                    os.renames(orig, new)
                except:
                    pass

    finally:
        if tempdir:
            shutil.rmtree(tempdir)
