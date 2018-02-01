#!/usr/bin/env python
"""
Scraper script for emuparadise.me

Usage
=====

```
fopina$ ./emuparadise.py -h
usage: emuparadise.py [-h] [--download] [--search] [--system SYSTEM] [--list]
                      ...

EmuParadise Scraper

positional arguments:
  QUERY/URL             Search QUERY if searching or ROM URL if retrieving
                        direct download link

optional arguments:
  -h, --help            show this help message and exit
  --download, -d        Retrieve direct download link
  --search, -s          Search
  --system SYSTEM, -t SYSTEM
                        Specify emulation system (to be used with --search)
  --list, -l            List IDs for supported emulation systems
```

Examples
========

Search
------

```
fopina$ ./emuparadise.py -s -t 2 silent hill
Silent Hill (E) ISO (Sony Playstation, id: 2) - 253M
/Sony_Playstation_ISOs/Silent_Hill_(E)/52771

Silent Hill [NTSC-U] ISO (Sony Playstation, id: 2) - 241M
/Sony_Playstation_ISOs/Silent_Hill_[NTSC-U]/37547

Silent Hill (Trial Version) (E) ISO (Sony Playstation, id: 2) - 46M
/Sony_Playstation_ISOs/Silent_Hill_(Trial_Version)_(E)/52772

Silent Hill (J) ISO (Sony Playstation, id: 2) - 252M
/Sony_Playstation_ISOs/Silent_Hill_(J)/53247

Silent Hill (Japan) (v1.0) ISO (Sony Playstation, id: 2) - 241M
/Sony_Playstation_ISOs/Silent_Hill_(Japan)_(v1.0)/176984

Silent Hill (Japan) (v1.1) ISO (Sony Playstation, id: 2) - 241M
/Sony_Playstation_ISOs/Silent_Hill_(Japan)_(v1.1)/176985

Found 6 roms
```

Direct Download
---------------

```
fopina$ ./emuparadise.py -d '/Sony_Playstation_ISOs/Silent_Hill_(E)/52771'
http://50.7.161.74/happyxhJ1ACmlTrxJQpol71nBc/may/PSX-PAL/Silent%20Hill%20%28E%29%20%5BSLES-01514%5D.7z
```

Directly to curl

```
fopina$ curl -O $(./emuparadise.py -d '/Sony_Playstation_ISOs/Silent_Hill_(E)/52771')
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  3  251M    3 8967k    0     0  1380k      0  0:03:06  0:00:06  0:03:00 1149k
```

Search to curl (feeling lucky??)

```
fopina$ curl -O $(./emuparadise.py -d $(./emuparadise.py -t 2 -s Silent Hill | head -2 | tail -1))
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0  251M    0  518k    0     0   354k      0  0:12:07  0:00:01  0:12:06  354k
```
"""

import requests
import re
import HTMLParser
from urlparse import urljoin

BASE_URL = 'http://www.emuparadise.me/'
SYSTEMS = {
    'Abandonware': 51, 'Acorn Archimedes': 58, 'Acorn BBC Micro': 59, 'Acorn Electron': 60,
    'Amiga': 4, 'Amiga CD': 52, 'Amiga CD32': 22, 'Amstrad CPC': 62, 'Android': 65,
    'Apple ][': 24, 'Atari 2600': 49, 'Atari 5200': 48, 'Atari 7800': 47, 'Atari 8-bit Family': 57,
    'Atari Jaguar': 50, 'Atari Lynx': 28, 'Atari ST': 63, 'Bandai Playdia': 56, 'Bandai Wonderswan': 39,
    'Bandai Wonderswan Color': 40, 'Capcom Play System 1': 54, 'Capcom Play System 2': 55,
    'Capcom Play System 3': 66, 'Commodore 64 (Tapes)': 34, 'Commodore 64 Preservation Project': 33,
    'Complete ROM Sets (Full Sets in One File)': 37, 'iPod Touch - iPhone': 45,
    'M.A.M.E. - Multiple Arcade Machine Emulator': 7, 'Microsoft XBox': 43, 'Miscellaneous': 46,
    'Neo Geo': 26, 'Neo Geo Pocket - Neo Geo Pocket Color (NGPx)': 38, 'Neo-Geo CD': 8,
    'Nintendo 64': 9, 'Nintendo DS': 32, 'Nintendo Entertainment System': 13,
    'Nintendo Famicom Disk System': 29, 'Nintendo Game Boy': 12, 'Nintendo Game Boy Color': 11,
    'Nintendo Gameboy Advance': 31, 'Nintendo Gamecube': 42, 'Nintendo Virtual Boy': 27,
    'Nintendo Wii': 68, 'Nokia N-Gage': 17, 'Panasonic 3DO (3DO Interactive Multiplayer)': 20,
    'PC Engine - TurboGrafx16': 16, 'PC Engine CD - Turbo Duo - TurboGrafx CD': 18, 'PC-FX': 64,
    'Philips CD-i': 19, 'PSP': 44, 'PSX on PSP': 67, 'ScummVM': 21, 'Sega 32X': 61, 'Sega CD': 10,
    'Sega Dreamcast': 1, 'Sega Game Gear': 14, 'Sega Genesis - Sega Megadrive': 6, 'Sega Master System': 15,
    'Sega NAOMI': 30, 'Sega Saturn': 3, 'Sharp X68000': 23, 'Sony Playstation': 2, 'Sony Playstation 2': 41,
    'Sony Playstation - Demos': 25, 'Sony Playstation - Old': 1069, 'Sony PocketStation': 53,
    'Super Nintendo Entertainment System (SNES)': 5, 'ZX Spectrum (Tapes)': 36, 'ZX Spectrum (Z80)': 35
}


class EmuParadise(object):
    referer = None
    h = HTMLParser.HTMLParser()

    def get_link(self, game_url):
        links = re.findall(
            '<a href="(/roms/get-download.php?.*?)" id="download-link"',
            self._get(game_url + '-download').content
        )
        if links:
            return self._get(self.h.unescape(links[0]), follow=False).headers['location']

    def search(self, query, system=0):
        return re.findall(
            '<div class="roms"><a .*?href="(.*?)">(.*?)</a>.*?<a href="\/roms\/roms\.php'
            '\?sysid=(\d+)".*?class="sysname">(.*?)</a>.*?<b>Size:</b> (.*?) .*?</div>',
            self._get(
                '/roms/search.php',
                data=dict(query=query, section='roms', sysid=system)
            ).content
        )

    def _get(self, url, follow=True, data=None):
        url = urljoin(BASE_URL, url)
        extra = dict(cookies=dict(downloadcaptcha='1'))
        if self.referer is not None:
            extra['headers'] = dict(referer=self.referer)
        if not follow:
            extra['allow_redirects'] = False
        if data is not None:
            extra['params'] = data
        self.referer = url
        return requests.get(url, **extra)


def parseargs():
    import argparse

    parser = argparse.ArgumentParser(description='EmuParadise Scraper')

    parser.add_argument('param', metavar='QUERY/URL', nargs=argparse.REMAINDER,
                        help='Search QUERY if searching or ROM URL if retrieving direct download link')
    parser.add_argument('--download', '-d', dest='download',
                        action='store_const', const=True, default=False,
                        help='Retrieve direct download link')
    parser.add_argument('--search', '-s', dest='search', action='store_const',
                        const=True, default=False,
                        help='Search')
    parser.add_argument('--system', '-t', dest='system', type=int, default=0,
                        help='Specify emulation system (to be used with --search)')
    parser.add_argument('--list', '-l', dest='list', action='store_const',
                        const=True, default=False,
                        help='List IDs for supported emulation systems')

    args = parser.parse_args()

    if not args.param:
        if args.search:
            parser.error('-s/--search requires a text query')
        if args.download:
            parser.error('-d/--download requires an URL')
    return args


def main():
    args = parseargs()
    if args.list:
        for system in sorted(SYSTEMS.items()):
            print('%s - %s' % (system[1], system[0]))

    if args.search:
        roms = EmuParadise().search(' '.join(args.param), system=args.system)
        for rom in roms:
            print('%s (%s, id: %s) - %s\n%s\n' % (rom[1], rom[3], rom[2], rom[4], rom[0]))
        print('Found %d rom%s' % (len(roms), '' if len(roms) == 1 else 's'))

    if args.download:
        print(EmuParadise().get_link(' '.join(args.param)))

if __name__ == '__main__':
    main()
