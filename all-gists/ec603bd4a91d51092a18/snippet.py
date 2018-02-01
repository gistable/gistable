#!/usr/bin/env python
# Script:      remove_jpg_if_raw_exists.py
#
# Description: This script looks in all sub directories for
#              pairs of JPG and RAW files.
#              For each pair found the JPG is moved to a
#              waste basket directory.
#              Otherwise JPG is kept.
#
# Author:      Thomas Dahlmann
# Modified by: Renaud Boitouzet

import os
import shutil

# define your file extensions here, case is ignored.
# Please start with a dot.
# multiple raw extensions allowed, single jpg extension only
raw_extensions = (".Dng", ".cR2", ".nef", ".crw")
jpg_extension = ".jPg"

# define waste basket directory here. Include trainling slash or backslash.
# Windows : waste_dir = "C:\path\to\waste\"
waste_dir = "/Users/marvin/Pictures/waste/"

##### do not modify below ##########

# find files
def locate(folder, extensions):
    '''Locate files in directory with given extensions'''
    for filename in os.listdir(folder):
        if filename.endswith(extensions):
            yield os.path.join(folder, filename)

# make waste basket dir
if not os.path.exists(waste_dir):
    os.makedirs(waste_dir)

# Make search case insensitive
raw_ext = tuple(map(str.lower,raw_extensions)) + tuple(map(str.upper,raw_extensions))
jpg_ext = (jpg_extension.lower(), jpg_extension.upper())

root=os.curdir
#find subdirectories
for path, dirs, files in os.walk(os.path.abspath(root)):
    print path
    raw_hash = {}
    for raw in locate(path, raw_ext):
        base_name = os.path.basename(raw)
        base_name = os.path.splitext(base_name)[0]
        raw_hash[base_name] = True

    # find pairs and move jpgs of pairs to waste basket
    for jpg in locate(path, jpg_ext):
        base_name = os.path.basename(jpg)
        base_name = os.path.splitext(base_name)[0]
        if base_name in raw_hash:
            jpg_base_name_with_ext = base_name + jpg_extension
            new_jpg = waste_dir + jpg_base_name_with_ext
            print "%s: %s = %s => %s" % (path, base_name, jpg, waste_dir)
            if os.path.exists(new_jpg):
                os.remove(jpg)
            else:
                shutil.move(jpg, new_jpg)
