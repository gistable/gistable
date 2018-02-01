#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import struct
from mutagen.easyid3 import EasyID3


def decode_gbk_from_unicode(s):
    l, f = [], []
    for item in s:
        i = ord(item)
        if i >= 0 and i <= 127:
            f.append('c')
            l.append(chr(i))
        else:
            f.append('B')
            l.append(i)
    r = struct.pack(''.join(f), *l)
    return r.decode('gbk')


def update_meta(f):
    audio = EasyID3(f)
    for (k, v_list) in audio.iteritems():
        try:
            audio[k] = [decode_gbk_from_unicode(v_list[0])]
        except:
            pass
    audio.save()


def main(directory):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.mp3'):
                print '> ', os.path.join(root, f)
                update_meta(os.path.join(root, f))


if __name__ == '__main__':
    f = u'/Users/patto/Music/lizhi/'
    main(f)