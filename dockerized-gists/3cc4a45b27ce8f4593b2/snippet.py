#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

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

"""Download tles from different places.
"""

# TODO:
# - add space-track.org

import urllib2
from datetime import datetime, timedelta
import logging
import logging.handlers
import socket
from trollsift.parser import compose

try:
    from pyorbital.orbital import Orbital
    from pyorbital.tlefile import ChecksumError
    import numpy as np
    import glob
except ImportError as err:
    print err
    Orbital = None


REF_DIR = "/tmp"
REF_PATTERN = "/data/arkiv/satellit/polar/orbital_elements/TLE/{date:%Y%m/tle-%Y%m%d}*.txt"


celestrak_weather = "http://celestrak.com/NORAD/elements/weather.txt"
celestrak_resource = "http://celestrak.com/NORAD/elements/resource.txt"
tle_info_weather = "http://www.tle.info/data/weather.txt"
tle_info_science = "http://www.tle.info/data/science.txt"
tle_info_tdrss = "http://www.tle.info/data/tdrss.txt"
eumetsat_metop_a_short = "http://oiswww.eumetsat.org/metopTLEs/html/data_out/latest_m02_short_tle.txt"
eumetsat_metop_a_long = "http://oiswww.eumetsat.org/metopTLEs/html/data_out/latest_m02_long_tle.txt"
eumetsat_metop_b_short = "http://oiswww.eumetsat.org/metopTLEs/html/data_out/latest_m01_short_tle.txt"
eumetsat_metop_b_long = "http://oiswww.eumetsat.org/metopTLEs/html/data_out/latest_m01_long_tle.txt"
drl_tle = "ftp://is.sci.gsfc.nasa.gov/ancillary/ephemeris/tle/drl.tle"


satellites = {"NOAA 19": (celestrak_weather, tle_info_weather),
              "NOAA 18": (celestrak_weather, tle_info_weather),
              "NOAA 15": (celestrak_weather, tle_info_weather),
              "TERRA": (celestrak_resource, tle_info_science, drl_tle),
              "AQUA": (celestrak_resource, tle_info_tdrss, drl_tle),
              ("SUOMI NPP", "NPP"): (drl_tle, celestrak_weather, tle_info_weather),
              "METOP-A": (eumetsat_metop_a_long, celestrak_weather, tle_info_weather, eumetsat_metop_a_short),
              "METOP-B": (eumetsat_metop_b_long, celestrak_weather, tle_info_weather, eumetsat_metop_b_short),
              }


max_age = timedelta(days=2)

MAILHOST = 'localhost'
FROM = 'me@me.org'
TO = ['you@you.org']
SUBJECT = 'TLE download errors on %s' % (socket.gethostname())


class BufferingSMTPHandler(logging.handlers.BufferingHandler):

    def __init__(self, mailhost, fromaddr, toaddrs, subject, capacity):
        logging.handlers.BufferingHandler.__init__(self, capacity)
        self.mailhost = mailhost
        self.mailport = None
        self.fromaddr = fromaddr
        self.toaddrs = toaddrs
        self.subject = subject
        self.setFormatter(
            logging.Formatter("[%(asctime)s %(levelname)-5s] %(message)s"))

    def flush(self):
        if len(self.buffer) > 0:
            try:
                import smtplib
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP(self.mailhost, port)
                msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (
                    self.fromaddr, ",".join(self.toaddrs), self.subject)
                for record in self.buffer:
                    s = self.format(record)
                    msg = msg + s + "\r\n"
                smtp.sendmail(self.fromaddr, self.toaddrs, msg)
                smtp.quit()
            except:
                self.handleError(None)  # no particular record
            self.buffer = []


def read_epoch(lines):
    epoch_year = 2000 + int(lines[1][18:20])
    epoch_day = float(lines[1][20:32])
    return (datetime(epoch_year, 1, 1) +
            timedelta(days=epoch_day - 1))


def append_checksum(line):
    """Computes the checksum for the current line.
    """
    check = 0
    for char in line:
        if char.isdigit():
            check += int(char)
        if char == "-":
            check += 1
    return line + str(check % 10)


def check_lines(lines, source):
    tle_lines = [lines[0]]
    for line in lines[1:]:
        clean_line = line.strip()
        if len(clean_line) == 68:
            logger.info("Looks like checksum is missing, appending it...")
            tle_lines.append(append_checksum(clean_line))
        elif len(clean_line) == 69:
            tle_lines.append(clean_line)
        else:
            logger.error("Spurious line from %s: %s", source, clean_line)
            tle_lines = []
    return tle_lines


def get_files(delta=30):
    """Get the tlefiles from the last delta days
    """

    now = datetime.utcnow()
    files = []
    for day in range(delta):
        pattern = compose(REF_PATTERN, {"date": now - timedelta(days=day)})
        files.extend(glob.glob(pattern))
    return files


def get_valid_orbit(platform_name, epoch):
    orb_nums = []
    for tle_file in sorted(get_files(), reverse=True):
        try:
            orb = Orbital(platform_name, tle_file=tle_file)
        except AttributeError:
            continue
        except ChecksumError:
            continue
        orb_nums.append(orb.get_orbit_number(epoch))

    return int(round(np.median(orb_nums)))


def get_last_valid_tle_lines(platform_name, epoch):
    if os.path.exists(os.path.join(REF_DIR, platform_name)):
        with open(os.path.join(REF_DIR, platform_name)) as fd:
            ref_lines = fd.readlines()
            ref_orb = Orbital(platform_name,
                              line1=ref_lines[1],
                              line2=ref_lines[2])
            if abs(epoch - ref_orb.tle.epoch) < timedelta(days=7):
                return ref_lines
            else:
                logger.info("cached TLE too old, refreshing")

    orbit = get_valid_orbit(platform_name, epoch)

    files = sorted(get_files(),
                   key=os.path.getctime)

    for tle_file in reversed(files):
        try:
            orb = Orbital(platform_name, tle_file=tle_file)
        except AttributeError:
            continue
        except ChecksumError:
            continue
        if orb.get_orbit_number(epoch) == orbit:
            lines = [orb.tle._platform, orb.tle._line1, orb.tle._line2]
            with open(os.path.join(REF_DIR, platform_name), "w") as fd:
                fd.write("\n".join(lines))
            return lines


def fix_tle_orbit(lines):
    if Orbital is None:
        logger.info("Pyorbital is missing, can't fix orbit number")
        return lines
    platform_name = lines[0]
    orb = Orbital(platform_name, line1=lines[1], line2=lines[2])
    epoch = orb.tle.epoch
    true_epoch = epoch
    # if too close from equator, fast forward to pole
    if abs(orb.get_lonlatalt(orb.tle.epoch)[1]) < 5:
        epoch += timedelta(days=1 / orb.tle.mean_motion / 4)

    orbnum = orb.get_orbit_number(epoch)

    ref_lines = get_last_valid_tle_lines(platform_name,
                                         epoch)

    ref_orb = Orbital(platform_name, line1=ref_lines[1], line2=ref_lines[2])
    ref_orbnum = ref_orb.get_orbit_number(epoch)

    if orbnum != ref_orbnum:
        logger.info("Spurious orbit number for %s: %d (should be %d)",
                    platform_name, orbnum, ref_orbnum)
        logger.info("replacing...")
        diff = ref_orbnum - orbnum

        lines[2] = lines[2][:63] + \
            "{0:05d}".format(orb.tle.orbit + diff) + lines[2][68:]
        lines[2] = append_checksum(lines[2][:-1])
    return lines


def find_tle_lines_in_file(sats, filename):
    with open(filename) as fd:
        lines = fd.read().strip().split("\n")
    satellite = sats[0]
    tle_lines = []
    for lineno, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line in sats:
            try:
                tle_lines = check_lines([satellite]
                                        + lines[lineno + 1:lineno + 3],
                                        filename)
            except IndexError:
                logger.error(
                    "Premature end of file from %s", filename)
                tle_lines = []
                break
    return tle_lines


if __name__ == '__main__':
    import sys
    import os
    from tempfile import mkstemp

    if len(sys.argv) != 2:
        print "Usage: %s output_file.tle" % sys.argv[0]
        sys.exit(1)

    logger = logging.getLogger("tle-dl")
    logger.setLevel(logging.DEBUG)
    mailhandler = BufferingSMTPHandler(MAILHOST, FROM, TO, SUBJECT, 500)
    mailhandler.setLevel(logging.WARNING)
    logger.addHandler(mailhandler)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(
        logging.Formatter("[%(asctime)s %(levelname)-5s] %(message)s"))
    logger.addHandler(ch)

    tles = []

    cache = {}

    for sats, sources in satellites.items():
        TLE_LINES = []
        most_recent = []
        if not isinstance(sats, tuple):
            sats = (sats, )
        satellite = sats[0]

        filename = sorted(glob.glob(os.path.join(os.path.dirname(sys.argv[1]),
                                                 "*")),
                          key=os.path.getctime)[-1]

        PREVIOUS = find_tle_lines_in_file(sats, filename)
        if PREVIOUS:
            epoch = read_epoch(PREVIOUS)
            most_recent.append((epoch, PREVIOUS))

        for source in sources:
            try:
                LINES = cache.setdefault(
                    source, urllib2.urlopen(source).read().strip().split("\n"))
            except urllib2.URLError:
                logger.warning("Can't reach %s", source)
                continue
            logger.debug("checking %s ...", source)
            if len(LINES) == 2:
                TLE_LINES = check_lines([satellite] + LINES, source)
            else:
                for lineno, line in enumerate(LINES):
                    clean_line = line.strip()
                    if clean_line in sats:
                        try:
                            TLE_LINES = check_lines([satellite]
                                                    +
                                                    LINES[
                                                        lineno + 1:lineno + 3],
                                                    source)
                        except IndexError:
                            logger.error(
                                "Premature end of file from %s", source)
                            TLE_LINES = []
                            break

            if not TLE_LINES:
                continue

            TLE_LINES = fix_tle_orbit(TLE_LINES)

            epoch = read_epoch(TLE_LINES)
            if datetime.utcnow() - epoch > max_age:
                logger.warning("tle for %s is too old (%s) on %s",
                               satellite, str(epoch), source)
                most_recent.append((epoch, TLE_LINES))
                TLE_LINES = []
            else:
                tles.extend(TLE_LINES)
                logger.info("OK, got tle for %s", satellite)
                break

        if not TLE_LINES:
            if most_recent:
                most_recent.sort()
                logger.warning("Couldn't find fresh tles for %s", satellite)
                logger.info("Taking the newest, from %s", most_recent[-1][0])
                tles.extend(most_recent[-1][1])
            else:
                logger.error("Couldn't find valid tles for %s", satellite)

    temp_name = mkstemp(dir=os.path.dirname(sys.argv[1]))[1]
    with open(temp_name, 'w') as fd:
        fd.write("\n".join(tles))
    os.chmod(temp_name, 0o644)
    os.rename(temp_name, sys.argv[1])

    logging.shutdown()
