#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import argparse
import subprocess
import os
import glob
from itertools import chain
import platform
import unicodedata

def download(url,
             video_formats='137/136/135/134/133',
             audio_formats='141/140/139',
             subtitle_languages='en,es'):

    download_program = 'youtube-dl'

    filename = subprocess.check_output([download_program, '--get-filename', url]).strip()
    base, _ = os.path.splitext(filename)

    if platform.system() == 'Darwin':
        # HACK: On Mac OS X certain characters in filenames (eg \xf3)
        # seem to cause weird behaviour where glob() won't find the file.
        # Changing to a unicode variant avoids this problem.
        base = unicodedata.normalize('NFD', base.decode('utf-8'))

    out = base + '.mkv'
    if os.path.exists(out):
        print '{0} already exists.'.format(out)
        return

    subprocess.call([download_program,
                    '-f', video_formats,
                    '--sub-lang', subtitle_languages, '--write-sub', '--write-auto-sub',
                    url])
    subprocess.call([download_program,
                    '-f', audio_formats,
                    url])

    files = glob.glob(base + '*')

    subprocess.call(['ffmpeg'] + list(chain(*[('-i', f) for f in files])) + [
                     '-vcodec', 'copy',
                     '-acodec', 'copy',
                     out])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download highest quality youtube video.')
    parser.add_argument('url', help='Video url.')
    args = parser.parse_args()

    download(args.url)
