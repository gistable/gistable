#!/usr/bin/env python
# -* - coding: utf-8 -*-
import argparse
import inspect
import eyed3
import eyed3.id3

def convertID3Encoding(audiofile, backup = False):
    tag = audiofile.tag
    if not tag:
        return
    for prop, value in inspect.getmembers(tag):
        if not isinstance(value, unicode):
            continue
        try:
            # ID3 tag (encoded in cp932) is decoded in Latin-1 by 'decodeUnicode' function
            # note: don't specify 'shift_jis' because fails to decode platform dependent characters
            setattr(tag, prop, value.encode('latin1').decode('cp932'))
        except:
            pass

    version = tag.version
    if tag.isV1() or version == eyed3.id3.ID3_V2_2:
        version = (2, 3, 0)

    try:
        tag.save(encoding = 'utf-16', version = version, backup = backup)
    except:
        # sometime fails to save tag due to using tags supported in ID3v2.4
        tag.save(encoding = 'utf-16', version = (2, 4, 0), backup = backup)

parser = argparse.ArgumentParser(description = 'convert ID3 tags of MP3 files from Latin-1 to UTF-16')
parser.add_argument('file', nargs = '+',
                    help = 'files to be converted')
parser.add_argument('--backup', action = 'store_true',
                    help = "backup file will be made in the same directory with '.orig' extentions")
args = parser.parse_args()

for filename in args.file:
    audiofile = eyed3.load(filename)
    convertID3Encoding(audiofile, args.backup)
    print "'%s' is converted" % filename
