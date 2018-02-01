#!/usr/bin/env python

import os
import sys
import glob
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

#
# MP3 playlist generator
#
# Generate an mp3 playlist file (.m3u), sorted by album track number.
#
# DEPENDENCIES
#
#   - Mutagen (http://code.google.com/p/mutagen/)
#
# NOTE: To install `mutagen`, run:
#
#   $ cd /path/to/mutagen/download/dir && python setup.py install
#
# USAGE
#
# You can pass directories two ways this script - as arguments or
# via standard input.
#
#   $ m3u.py /AphexTwin/Drukqs
#
# or multiple directories:
#
#   $ find /dir/Music -type d -links 2 | m3u.py -
#
# Author: Jon LaBelle <jon@tech0.com>
# Date: Sun Jul 28 2013 06:27:42 GMT-0500 (CDT)
#

def create_m3u(dir="."):

    try:
        print "Processing directory '%s'..." % dir

        playlist = ''
        mp3s = []
        glob_pattern = "*.[mM][pP]3"

        os.chdir(dir)

        for file in glob.glob(glob_pattern):
            if playlist == '':
                playlist = EasyID3(file)['album'][0] + '.m3u'

            meta_info = {
                'filename': file,
                'length': int(MP3(file).info.length),
                'tracknumber': EasyID3(file)['tracknumber'][0].split('/')[0],
            }

            mp3s.append(meta_info)

        if len(mp3s) > 0:
            print "Writing playlist '%s'..." % playlist

            # write the playlist
            of = open(playlist, 'w')
            of.write("#EXTM3U\n")

            # sorted by track number
            for mp3 in sorted(mp3s, key=lambda mp3: int(mp3['tracknumber'])):
                of.write("#EXTINF:%s,%s\n" % (mp3['length'], mp3['filename']))
                of.write(mp3['filename'] + "\n")

            of.close()
        else:
            print "No mp3 files found in '%s'." % dir

    except:
        print "ERROR occured when processing directory '%s'. Ignoring." % dir
        print "Text: ", sys.exc_info()[0]

def main(argv=None):
    if argv is None:
        argv = sys.argv

    # directories containing music files
    dirs = []

    if len(sys.argv) == 2 and sys.argv[1] == '-':
    # we do not have command line arguments, so read from STDIN
        for line in sys.stdin:
            dirs.append(line.strip())
    else:
    # passed in directories on the command line
        for dir in sys.argv[1:]:
            dirs.append(dir)

    # for each directory passed to us, go
    # to it and make the M3U out of the
    # MP3 files there
    for dir in dirs:
        create_m3u(dir)

    return 0

# if name == "main":
sys.exit(main())