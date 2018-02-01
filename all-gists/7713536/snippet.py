#!/usr/bin/env python2

"""
.SM rating fixer thingy!
========================

Usage:
Just put the file in the folder with the things you need fixed and run it!

You can also give it an argument on the command line to specify the path.

This takes the ratings, divides by 1.5, and writes the files out. Since I'm a
nice guy it also saves a .old with the original file contents, in case I
really screwed anything up!

Requires Python 2.7.x, probably works fine with 3.x if you use 2to3.
"""

import os
import sys
import re
import math

def processSimfileSM(content, write_file):
    # copy so we don't screw with the original data
    content = list(content)

    title = ""
    for idx, line in enumerate(content):
        if line.find("#TITLE:") == 0:
            title = line[line.find(":")+1:line.find(";")]

        if line.find("#NOTES") != 0:
            continue

        # XXX: This is an assumption and not a requirement of the SM format.
        # Hand-edited files may break this, although I don't have any that do.
        # I think that we play it safe enough to not cause any damage!
        diffname = content[idx+3]

        pos = re.search("\w", diffname)
        if not pos:
            continue

        diffname = diffname[pos.start():diffname.find(":")]

        # XXX: Also an assumption.
        # rating is always the 4th line after #NOTES
        diffline = content[idx+4]

        # find the number...
        pos = re.search("\d", diffline)
        if not pos:
            continue

        # and trim everything down
        diffline = diffline[pos.start():diffline.find(":")]
        diffline = int(diffline) # convert to int
        newdiff = max(round(diffline / 1.5), 1)

        content[idx+4] = "     %d:\n" % newdiff

        print "%s (%s) re-rated from %d to %d" % \
            (title, diffname, diffline, newdiff)

    return content

def writeFile(path, content):
    print "Writing: %s" % path
    with open(path, 'w') as f:
        f.write(''.join(content))

def processDirectory(args, dirname, filenames):
    write_file = True
    for filename in filenames:
        name, ext = os.path.splitext(filename)
        if ext == ".sm":
            path = os.path.join(dirname, filename)
            content = list()
            print "Reading %s" % path

            with open(path, 'r') as f:
                content = f.readlines()

            new_content = processSimfileSM(content, write_file)

            # write backup file and replace the original
            if write_file:
                writeFile(path, ''.join(new_content))
                writeFile(path + ".old", ''.join(content))

def main():
    if len(sys.argv) >= 2:
        base_dir = sys.argv[1]
    else:
        base_dir = "."

    os.path.walk(base_dir, processDirectory, None)

main()
