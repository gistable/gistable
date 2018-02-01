#!/usr/bin/env python
from __future__ import print_function

import sys
import subprocess
import argparse
import textwrap
import signal

stations = {
    "bagel": {
        "url": "http://somafm.com/bagel.pls",
        "name": "BAGeL Radio",
        "category": "alternative",
        "description": "What alternative rock radio should sound like.",
    },
    "beatblender": {
        "url": "http://somafm.com/beatblender.pls",
        "name": "Beat Blender",
        "category": "electronica",
        "description": "A late night belnd of deep-house and downtempo chill.",
    },
    "bootliquor": {
        "url": "http://somafm.com/bootliquor.pls",
        "name": "Boot Liquor",
        "category": "americana",
        "description": "Americana Roots music for Cowhands, Cowpokes and Cowtippers",
    },
    "brfm": {
        "url": "http://somafm.com/brfm130.pls",
        "name": "Black Rock FM",
        "category": "eclectic",
        "description": "From the Playa to the world, for the 2012 Burning Man festival.",
    },
    "cliqhop": {
        "url": "http://somafm.com/cliqhop.pls",
        "name": "cliqhop idm",
        "category": "electronica",
        "description": "Blips 'n' beeps backed mostly w/ beats. Intelligent Dance Music.",
    },
    "covers": {
        "url": "http://somafm.com/covers.pls",
        "name": "Covers",
        "category": "eclectic",
        "description": "Just covers. Songs you know by artists you don't We've got you covered.",
    },
    "digitalis": {
        "url": "http://somafm.com/digitalis.pls",
        "name": "Digitalis",
        "category": "electronica/alternative",
        "description": "Digitaly affected analog rock to calm the agitated heart.",
    },
    "doomed": {
        "url": "http://somafm.com/doomed.pls",
        "name": "Doomed",
        "category": "ambient/industrial",
        "description": "Dark industrial/ambient music for tortured souls.",
    },
    "dronezone": {
        "url": "http://somafm.com/dronezone130.pls",
        "name": "Drone Zone",
        "category": "ambient",
        "description": "Served best chilled. Safe with most medications. Atmospheric texture with minimal beats.",
    },
    "dubstep": {
            "url": "http://somafm.com/dubstep.pls",
        "name": "Dub Step Beyond",
        "category": "electronica",
        "description": "Dubstep. Dub and Deep Bass. May damage speakers at high volume.",
    },
    "folkfwd": {
            "url": "http://somafm.com/folkfwd.pls",
        "name": "Folk Forward",
        "category": "folk/alternative",
        "description": "Indie Folk. Alt-folk and the occasional folk classics.",
    },
    "groovesalad": {
            "url": "http://somafm.com/groovesalad130.pls",
        "name": "Groove Salad",
        "category": "ambient/electronica",
        "description": "A nicely chilled plate of ambient/downtempo beats and grooves.",
    },
    "illstreet": {
            "url": "http://somafm.com/illstreet130.pls",
        "name": "Illionois Street Lounge",
        "category": "lounge",
        "description": "Classic bachelor pad. Playful exotica and vintage music of tomorrow.",
    },
    "indiepop": {
            "url": "http://somafm.com/indiepop130.pls",
        "name": "Indie Pop Rocks!",
        "category": "alternative",
        "description": "New and classic favorite indie pop tracks.",
    },
    "lush": {
            "url": "http://somafm.com/lush130.pls",
        "name": "Lush",
        "category": "electronica",
        "description": "Sensuous and mellow vocals, mostly female, with an electronic influence",
    },
    "missioncontrol": {
            "url": "http://somafm.com/missioncontrol.pls",
        "name": "Mission Control",
        "category": "ambient/electronica",
        "description": "Celebrating NASA and Space Explorers everywhere.",
    },
    "poptron": {
            "url": "http://somafm.com/poptron.pls",
        "name": "PopTron",
        "category": "alternative",
        "description": "Electropop and indie dance rock with sparkle and pop",
    },
    "secretagent": {
            "url": "http://somafm.com/secretagent130.pls",
        "name": "Secret Agent",
        "category": "lounge",
        "description": "The soundtrack for your stylish, mysterious, dangerous life. For Spies and PIs too!",
    },
    "sf1033": {
            "url": "http://somafm.com/sf1033.pls",
        "name": "SF 10-33",
        "category": "ambient/news",
        "description": "Ambient music mixed with the sounds of San Francisco public safety radio traffic.",
    },
    "sonicuniverse": {
            "url": "http://somafm.com/sonicuniverse192.pls",
        "category": "jazz",
        "name": "Sonic Universe",
        "description": "Transcending the world of jazz eclectic, avant-garde takes on tradition",
    },
    "spacestation": {
            "url": "http://somafm.com/spacestation130.pls",
        "name": "Space Station Soma",
        "category": "electronica",
        "description": "Tune in, turn on, space out. Spaced-out ambient and mid-tempo electronica.",
    },
    "suburbsofgoa": {
            "url": "http://somafm.com/suburbsofgoa130.pls",
        "name": "Suburbs of Goa",
        "category": "world",
        "description": "Desi-influenced Asian world beats and beyond.",
    },
    "sxfm": {
            "url": "http://somafm.com/sxfm.pls",
        "name": "South by Soma",
        "category": "alternative",
        "description": "Music from bands who will be performing at SXSW, one of the biggest and best music festivals in the world. [explicit]",
    },
    "thetrip": {
            "url": "http://somafm.com/thetrip.pls",
        "name": "Tag's Trip",
        "category": "electronica",
        "description": "Progressive house / trance. Tip top tunes.",
    },
    "u80s": {
            "url": "http://somafm.com/u80s130.pls",
        "name": "Underground 80s",
        "category": "alternative/electronica",
        "description": "Early 80s UK Synthpop and a bit of New Wave.",
    },
}

parser = argparse.ArgumentParser(description="Play radio stations from SomaFM. Be sure to donate often at http://somafm.com/support/.")
parser.add_argument("station", help="The tag of the station to play.", default=None, nargs='?')
parser.add_argument("--category", help="Filter by category")
parser.add_argument("--player", help="Name of the binary to play. Default mplayer.", default="mplayer")

class colors:
    COLORS = {
        'header': '\033[95m',
        'blue': '\033[94m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'endc': '\033[0m',
    }
    def __init__(self, color, out=sys.stdout):
        self.color = color
        self.out = out

    def __enter__(self):
        self.out.write(self.COLORS[self.color])

    def __exit__(self, type, value, traceback):
        self.out.write(self.COLORS['endc'])

def main():
    args = parser.parse_args()
    if args.station:
        if args.station not in stations:
            with colors("red", sys.stderr):
                sys.stderr.write("Sation {0} not found.\n".format(args.station))
            sys.exit(1)

        cmd = [args.player, stations[args.station]['url']]
        proc = subprocess.Popen(cmd)
        try:
            proc.communicate()
        except KeyboardInterrupt:
            # Avoid capturing the terminal by waiting for mplayer to die
            # gracefully.
            proc.send_signal(signal.SIGINT)
            proc.wait()
    else:
        col1_length = max(
            [len(a) + len(stations[a]['category']) for a in stations]
        ) + 2
        col2_length = 80 - col1_length
        col2_first_line_fmt = "{{0:{0}}}".format(col2_length)
        col2_nth_line_fmt = " " * col1_length + col2_first_line_fmt
        for key in sorted(stations):
            stat = stations[key]
            if args.category and args.category not in stat['category']:
                continue
            width = len(key) + len(stat['category']) + 2
            print(key, end=' ')
            with colors("yellow"):
                print(stat['category'], end=' ')
            with colors("green"):
                #print(' ' * (col1_length - width), end='')
                lines = textwrap.wrap(stat['description'], 80 - width)
                print(lines[0])
                for line in lines[1:]:
                    print(" " * width, end='')
                    print(line)

if __name__ == "__main__":
    main()
