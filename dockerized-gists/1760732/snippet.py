#!/usr/bin/env python3
# coding: utf-8

# playlist-dl  This program can be used to convert YouTube playlists to M3U
#              playlists
# Copyright (C) 2012  Jakob Kramer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import tempfile

from argparse import ArgumentParser
from subprocess import check_output, call, CalledProcessError

from lxml.html import parse

__version__ = '0.2.1'

FORMATS = {
    'mp4': {
        480: 18,
        720: 22,
        1080: 37
    },
    'webm': {
        480: 43,
        720: 45
    }
}

VIEWER = 'vlc'
CSS = 'li.playlist-video-item > a:nth-child(1)'

def yt2m3u(playlist_url, format=FORMATS['mp4'][480]):
    root = parse(playlist_url).getroot()
    root.make_links_absolute(root.base_url)
    yt_urls = [link.attrib['href'] for link in root.cssselect(CSS)]

    try:
        return check_output(['youtube-dl', '-f', str(format), '-g']+yt_urls,
                            universal_newlines=True)
    except CalledProcessError:
        return [] # nothing to do, errors are handled below

def main():
    parser = ArgumentParser(description='Play a YouTube playlist without Flash.')
    parser.add_argument('url', help='URL of the playlist.')
    parser.add_argument('-f', '--format', dest='format', choices=FORMATS.keys(),
                        help='The format which will be used to stream the '
                        'video  (default: mp4)', default='mp4')
    parser.add_argument('-q', '--quality', type=int, dest='quality', default=480,
                        choices=[480, 720, 1080], help='The quality which will'
                        ' be used when streaming.  (default: 480p)')
    parser.add_argument('-s', '--save', dest='filename', help='Only save the '
                        'playlist and quit.')
    args = parser.parse_args()

    if args.quality not in FORMATS[args.format]:
        parser.error('This format does not support the specified quality.')

    if args.filename is not None:
        with open(args.filename, 'w') as f:
            f.writelines(yt2m3u(args.url, FORMATS[args.format][args.quality]))

        return

    with tempfile.NamedTemporaryFile('w', suffix='.m3u') as f:
        f.writelines(yt2m3u(args.url, FORMATS[args.format][args.quality]))
        f.flush()
        os.fsync(f.fileno())
        call([VIEWER, f.name])


if __name__ == '__main__':
    main()