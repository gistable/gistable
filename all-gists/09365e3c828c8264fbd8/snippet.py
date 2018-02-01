#!/usr/bin/env python

"""
Display gluster traffic
This tool uses gluster profiling feature, parsing cumulative statistics.

To understand correctly the results, you have to divide overall write statistics with number of replicas.
Also striped volumes needs to be taken in mind - overall statistics just print sum of all bricks
read/written bytes.

First output prints statistics since the beginning of profiling
"""

import subprocess
import sys
import os
from xml.dom import minidom
import logging
import argparse
import time
import datetime
import curses

parser = argparse.ArgumentParser(
    description='Display gluster traffic',
    epilog='This tool uses gluster profiling feature, parsing intervals, updated every time gluster volume profile runs.\
    Take care that only this tool should run gluster volume profile command otherwise no stats will be shown.'
)
parser.add_argument(dest='volume', help="Volume name (use 'all' for all volumes, all implies --no-bricks)")
parser.add_argument('-b', '--batch', dest='batch', action='store_true', help="Batch output, don't update")
parser.add_argument('--no-bricks', dest='no_bricks', action='store_true', help="Don't print per-brick statistics")
parser.add_argument('--bytes', dest='bytes', action='store_true', help="Print output in bytes/s instead of MB/s")
parser.add_argument('--kb', '--kbytes', dest='kbytes', action='store_true', help="Print output in KB/s instead of MB/s")
parser.add_argument('-i', '--interval', dest='interval', type=int, default=1, help="Update interval (default 1 second)")
parser.add_argument('--no-curses', dest='no_curses', action='store_true', help="Don't use curses interface")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help="Be verbose")
parser.add_argument('--debug', dest='debug', action='store_true', help="Debug output")
args = parser.parse_args()

logging.basicConfig(level=logging.WARN)
lg = logging.getLogger()

if args.batch:
    args.no_curses = True

if args.bytes:
    units = 'b/s'
elif args.kbytes:
    units = 'KB/s'
else:
    units = 'MB/s'

# Initialize curses
if not args.no_curses:
    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(1)

if args.verbose:
    lg.setLevel(logging.INFO)

if args.debug:
    lg.setLevel(logging.DEBUG)

# Failed volumes
error = []

# Volume statistics from last run
volStats = {}

def main():
    """
    Main entrance
     * get stats in the loop
    """
    try:
        while True:
            try:
                stats = []
                if args.volume == 'all':
                    args.no_bricks = True
                    volumes = getVolumes()
                    for vol in volumes:
                        if vol not in error:
                            stats.append(getVolumeStats(vol))
                else:
                    stats.append(getVolumeStats(args.volume))

                try:
                    printOutput(stats)
                except curses.error as e:
                    cursesCleanup()
                    lg.error("Can't render curses (maybe terminal too small?): %s" % e)
                    sys.exit(1)
            except IOError:
                # Refresh screen if interrupted during screen resize
                if not args.no_curses:
                    stdscr.refresh()
                else:
                    pass
            if args.batch:
                raise KeyboardInterrupt

            t0 = datetime.datetime.now()
            t_delta = t0
            t_seconds = 0
            while t_seconds < args.interval:
                # Exit on q key press, don't block
                if not args.no_curses:
                    stdscr.nodelay(1)
                    key = stdscr.getch()
                    keyEvent(key)
                t_seconds = (datetime.datetime.now() - t0).seconds
                time.sleep(0.1)
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        cursesCleanup()

def cursesCleanup():
    """
    Cleanup curses
    """
    if not args.no_curses:
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()

def keyEvent(key):
    """
    Do action on specified key event
    """
    # 'q' key
    if key == 113:
        raise KeyboardInterrupt
    # Screen resize
    elif curses.KEY_RESIZE:
        stdscr.refresh()

def printOutput(stats):
    """
    Print statistics output with or without Curses
    """
    head = " Average statistics, interval %s seconds " % args.interval
    foot = " Press q to exit "

    totalRead  = 0
    totalWrite = 0

    if not args.no_curses:
        stdscr.clear()
        stdscr.border(0)
        ymax,xmax = stdscr.getmaxyx()
        stdscr.addstr(0, xmax-len(head)-2, head)
        stdscr.addstr(ymax-1, xmax-len(foot)-2, foot)

        y = 2
        x = 4
        for vol in stats:
            if not vol:
                continue

            stdscr.addstr(y, x, "Volume: %s" % vol['volume'])
            y += 1
            x += 1

            stdscr.addstr(y, x, "Total read:  %s %s" % (convertUnits(vol['read']), units))
            y += 1
            stdscr.addstr(y, x, "Total write: %s %s" % (convertUnits(vol['write']), units))
            y += 2

            if not args.no_bricks:
                for name, brick in sorted(vol['bricks'].iteritems()):
                    stdscr.addstr(y, x, "Brick: %s" % name)
                    y += 1
                    stdscr.addstr(y, x+2, "Read:  %s %s" % (convertUnits(brick['read']), units))
                    y += 1
                    stdscr.addstr(y, x+2, "Write: %s %s" % (convertUnits(brick['write']), units))
                    y += 2

            x -= 1
            totalRead  += vol['read']
            totalWrite += vol['write']

        # Overall statistics for all volumes
        if len(stats) > 1:
            stdscr.addstr(2, xmax-30, "Overall read:  %s %s" % (convertUnits(totalRead), units))
            stdscr.addstr(3, xmax-30, "Overall write: %s %s" % (convertUnits(totalWrite), units))

        stdscr.refresh()
    else:
        print head
        for vol in stats:
            if not vol:
                continue

            print "Volume: %s" % vol['volume']
            print " Total read:  %s %s" % (convertUnits(vol['read']), units)
            print " Total write: %s %s" % (convertUnits(vol['write']), units)

            if not args.no_bricks:
                for name, brick in sorted(vol['bricks'].iteritems()):
                    print " Brick: %s" % name
                    print "  Read:  %s %s" % (convertUnits(brick['read']), units)
                    print "  Write: %s %s" % (convertUnits(brick['write']), units)

            print ""
            totalRead  += vol['read']
            totalWrite += vol['write']
        print "Overall read:  %s %s" % (convertUnits(totalRead), units)
        print "Overall write: %s %s" % (convertUnits(totalWrite), units)
        print ""

def convertUnits(num):
    """
    Convert bytes to specified units
    """
    if units == 'MB/s':
        return num / 1024 / 1024
    elif units == 'KB/s':
        return num / 1024
    else:
        return num

def getVolumes():
    """
    Get list of available volumes
    """
    volumes = []
    p = subprocess.Popen('/usr/sbin/gluster volume list', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    for vol in p.stdout.readlines():
        volumes.append(vol.replace('\n', ''))
    retval = p.wait()
    return volumes

def getVolumeStats(volume):
    """
    Get per-volume statistics
    """
    stats = {}
    out = None

    p = subprocess.Popen('/usr/sbin/gluster volume profile %s info --xml' % volume, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    out = p.stdout.read()
    retval = p.wait()

    xml = minidom.parseString(out)

    # Can't get volume or it doesn't have profiling started
    ret = int(xml.getElementsByTagName('opRet')[0].toxml().replace('<opRet>', '').replace('</opRet>', ''))
    if ret != 0:
        if args.no_curses:
            lg.error("Can't get profile data for volume %s" % volume)
        else:
            stdscr.clear()
            stdscr.border(0)
            stdscr.addstr(2, 2, "ERROR: Can't get profile data for volume %s" % volume)
            stdscr.addstr(0, 2, " Press any key to continue or q to quit ")
            stdscr.refresh()
            # Wait for key input
            key = stdscr.getch()
            keyEvent(key)
        error.append(volume)
        return False

    global volStats
    try:
        volStats[volume]
    except:
        volStats[volume] = {}

    duration   = 0
    overallRead  = 0
    overallWrite = 0

    stats['bricks'] = {}
    bricks = xml.getElementsByTagName('brick')
    for brick in bricks:
        interval = brick.getElementsByTagName('cumulativeStats')[0]
        brickName = brick.getElementsByTagName('brickName')[0].toxml().replace('<brickName>', '').replace('</brickName>', '')
        totalRead  = int(interval.getElementsByTagName('totalRead')[0].toxml().replace('<totalRead>', '').replace('</totalRead>', ''))
        totalWrite = int(interval.getElementsByTagName('totalWrite')[0].toxml().replace('<totalWrite>', '').replace('</totalWrite>', ''))
        duration    = int(interval.getElementsByTagName('duration')[0].toxml().replace('<duration>', '').replace('</duration>', ''))

        try:
            stats_old = volStats[volume][brickName]
        except KeyError:
            stats_old = {
                'duration'  : 0,
                'totalRead' : 0,
                'totalWrite': 0,
            }

        # Update last statistics result
        volStats[volume][brickName] = {
            'duration'  : duration,
            'totalRead' : totalRead,
            'totalWrite': totalWrite,
        }

        # Update current results
        totalRead  -= stats_old['totalRead']
        totalWrite -= stats_old['totalWrite']
        duration   -= stats_old['duration']

        # Division by zero, huh?
        if duration == 0:
            duration = 1

        brickStat = {
            'read' : totalRead / duration,
            'write': totalWrite / duration,
        }
        stats['bricks'][brickName] = brickStat

        overallRead  += totalRead
        overallWrite += totalWrite

    stats['read']  = overallRead / duration
    stats['write'] = overallWrite / duration
    stats['total'] = stats['read'] + stats['write']
    stats['duration'] = duration
    stats['volume'] = volume

    return stats

if __name__ == '__main__':
    main()