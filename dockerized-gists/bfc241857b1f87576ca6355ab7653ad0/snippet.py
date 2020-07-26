# -*- coding: utf-8 -*-

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

# Author: Manuel Kaufmann <humitos@gmail.com>
# Date: 29 October 2016
# Release: 0.5


# DESCRIPTION:
#
# This program allows you to do not listen to Spotify Ads withuot having a paid
# account. It's not too much intelligent right now, so you have to add the
# Artists you usually listen to or the name of the Spotify Ads you want to mute.
#
# How it works? It just mute the sound system when it detects an Ads is being
# played. How? By reading the window's title and check against all the known
# names and Ads you have defined and using some dumb pre-defined rules that fail
# in some cases.

from __future__ import division, print_function, unicode_literals

import commands
import os
import sys
import time

HOSTNAME = commands.getoutput('hostname')
TERMINAL_ENCODING = commands.getoutput('locale charmap')
WMCTRL_WINDOW_LIST = "wmctrl -l -x | grep 'spotify.Spotify' | grep -v 'grep'"
MUTE_COMMAND = "amixer -q -D pulse sset Main mute"
UNMUTE_COMMAND = "amixer -q -D pulse sset Main unmute"
SPOTIFY_OPEN_COMMAND = "ps -ef | grep Spotify | grep -v grep | wc -l"

MUTED = False
SPOTIFY_OPENED = False
SONGS_PLAYED = []

# Time in seconds
SLEEP_BEFORE_UNMUTE = 1.5
SLEEP_BETWEEN_EACH_CHECK = 0.1
SLEEP_WHEN_SPOTIFY_CLOSED = 5

# Define the names of the Artists, Songs, etc you usually listen to here
KNOWN_TITLES = (
    # Titles that I found with problems matching dumb rules
    ['Emir Kusturica'],
    ['Jarabe De Palo'],
    ['Bob Marley'],
    ['Queen'],
    ['Soda Stereo'],

    # Titles I want to be sure that are valid
    map(
        lambda x: '- {}'.format(x),
        ['Remained', 'Extended Version', 'En Vivo', 'MTV Unplugged', 'Acoustic', 'Versión Acústica', 'Live',
         'Directo', 'directo', 'unplugged', 'en directo', 'Unplugged Version', 'Live/Unplugged', 'Instrumental',
         'Remainizado', 'BBC'],
    ),
    # ...
)

# Define the names of the Ads you usually listen to and want to avoid here
ADS_TITLES = (
    # ...
    ['REYKON'],
)


def mute():
    global MUTED
    MUTED = True
    os.system(MUTE_COMMAND)


def unmute():
    global MUTED
    MUTED = False
    os.system(UNMUTE_COMMAND)


def is_spotify_opened():
    global SPOTIFY_OPENED
    output = commands.getoutput(SPOTIFY_OPEN_COMMAND)
    SPOTIFY_OPENED = bool(int(output))  # 0 is closed
    return SPOTIFY_OPENED


def is_known_title(spotify_title):
    if spotify_title.isupper():
        # most of the ads are upper case
        return False

    if len(spotify_title.split()) == 1:
        # some of the ads are just one word
        return False

    # check for known Ads
    for title in ADS_TITLES:
        for t in title:
            if t in spotify_title:
                return False

    if len(spotify_title.split(' - ')) == 2:
        # most of the songs are in the form "Artist - Title"
        return True

    # check for known Artists or Songs
    for title in KNOWN_TITLES:
        for t in title:
            if t in spotify_title:
                return True
    return False


def check_spotify_ads():
    output = commands.getoutput(WMCTRL_WINDOW_LIST)
    try:
        output = output.decode(TERMINAL_ENCODING)
        _, spotify_title = output.split(HOSTNAME)
    except (ValueError, UnicodeDecodeError) as e:
        print('*** ERROR: {} ***'.format(e))
        print('*** Command Output: {} ***'.format(output))
        return

    spotify_title = spotify_title.strip()
    known_title = is_known_title(spotify_title)
    if (spotify_title not in SONGS_PLAYED and known_title) or (not MUTED and not known_title):
        print('Playing:', spotify_title)

    if spotify_title not in SONGS_PLAYED and known_title:
        SONGS_PLAYED.append(spotify_title)

    if known_title:
        if MUTED:
            time.sleep(SLEEP_BEFORE_UNMUTE)  # the window title changes before the song starts
            unmute()
    else:
        if not MUTED:
            print('Sound MUTED.')
            mute()


if __name__ == '__main__':
    try:
        while True:
            if not is_spotify_opened():
                print('Spotify not running. Sleeping...')
                time.sleep(SLEEP_WHEN_SPOTIFY_CLOSED)
                continue

            check_spotify_ads()
            time.sleep(SLEEP_BETWEEN_EACH_CHECK)
    except KeyboardInterrupt:
        if MUTED:
            print('\nUnmuting...', end=' ')
            unmute()
        print('\nBye.')
        sys.exit(0)
