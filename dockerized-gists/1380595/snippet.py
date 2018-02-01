#!/usr/bin/python2

import os
import shutil
import errno
import unicodedata
import time
import traceback
from mutagen.id3 import ID3

ASCIIAZE_FILENAMES = True
# chars not allowed in filenames
illegal_chars = u'/\?=+<>:;"*|!@#$%^&*'

def has_chars(raw, bad_chars):
    for c in bad_chars:
        if c in raw:
            return True;
    return False;

def replace_illegal_chars(raw):
    return ''.join([c in illegal_chars and '_' or c for c in raw])

def sanitize(s):
    if has_chars(s):
        return replace_illegal_chars(s)
    return s

def unicode2asci(s):
    if not ASCIIAZE_FILENAMES:
        return s
    nkfd_form = unicodedata.normalize('NFKD', s)
    return u''.join([c for c in nkfd_form if not unicodedata.combining(c)])

def get_id3tag(id3frame, tagname):
    frame = id3frame[tagname]
    try:
        return frame.text[0]
    except Exception, e:
        print traceback.format_exc()
        return 'Unknown'

def organiseMP3(tempFileName, saveToDir=r'saved_music'):
    try:
        id3 = ID3(tempFileName)
        print "="*60
        try:
            print id3.pprint().encode('us-ascii', 'xmlcharrefreplace')
        except Exception, e:
            print e, traceback.format_exc()
            repr (id3.pprint())

        title = get_id3tag(id3, 'TIT2') # title
        artist = get_id3tag(id3, 'TPE1') # artist
        album = get_id3tag(id3, 'TALB') # album
        track = get_id3tag(id3, 'TRCK') # track number

        # if track in the form of 02/12 then extract first number only
        if track and u'/' in track:
            track = track.split('/')[0]
        if track:
            track = track.zfill(2) # zero fill, i. e. '1' >> '01'
        if track and track != 'Unknown':
            track += ' - '

        fileName = "%s%s.mp3" % (track, unicode2asci(title))
        songDir = os.path.join(saveToDir, unicode2asci(artist), unicode2asci(album))

        try:
            if not os.path.exists(songDir):
                os.makedirs(songDir)
        except OSError, e:
            print e, traceback.format_exc()
        target = os.path.join(songDir, unicode2asci(fileName))

        # if file already exists, then add some random chars to make it unique
        if os.path.exists(target):
            target_chunks = os.path.splitext(target)
            target = target_chunks[0] + time.time() + target_chunks[1]
        shutil.copy(tempFileName, target)

        print "Pwn'd an MP3 file: %s" % (target)

    except Exception, e:
        print e, traceback.format_exc()
