#!/usr/bin/env python
#
# Writes task start/stop times to a timelog formatted file.
# You might need to adjust LEDGERFILE, or set the TIMELOG environment variable.
#
# Example reports, after using start/stop on a task:
# ledger -f /path/to/timelog.ledger print
# ledger -f /path/to/timelog.ledger register
#
# Projects, tags, and UUIDs are fully supported and queryable from ledger.
#
#
# 2015-03-05 wbsch
#   - Now with "I forgot to start/stop this task!" convenience features:
#       "task $id start $x"
#       "task $id stop $x"
#       "task $id done $x"
#     Where $x is the time in minutes you want the entry in your timelog
#     file to be backdated. Note that this is not properly displayed in
#     Taskwarrior itself, but only in your timelog file.
#
#     Note: This will only work on Taskwarrior 2.4.2+ due to a bug in
#           earlier versions. The basic time tracking functionality will
#           work on 2.4.1+.
#
#
# May the Holy Python forgive me for this mess.
#

import calendar
import json
import os
import re
import sys
from datetime import datetime
from datetime import timedelta


LEDGERFILE = "%s/.task/hooks/timetrack.ledger" % os.getenv('HOME')

if 'TIMELOG' in os.environ:
    LEDGERFILE = os.environ['TIMELOG']


def adjust_date(d, adjust_by):
    if not isinstance(d, datetime):
        d = tw_to_dt(d)
    d -= timedelta(minutes=int(adjust_by))
    return d

def tw_to_dt(s):
    """ Taskwarrior JSON date ---> datetime object. """
    return datetime.strptime(s, "%Y%m%dT%H%M%SZ")

def dt_to_tw(d):
    """ datetime object ---> Taskwarrior JSON date. """
    return d.strftime("%Y%m%dT%H%M%SZ")


old = json.loads(sys.stdin.readline())
new = json.loads(sys.stdin.readline())

annotation_added = ('annotations' in new and not 'annotations' in old) \
                    or \
                 ('annotations' in new and 'annotations' in old and \
                  len(new['annotations']) > len(old['annotations']))


# task started
if ('start' in new and not 'start' in old) and annotation_added:
    new['annotations'].sort(key=lambda anno: anno['entry'])
    m = re.match('^[0-9]+$', new['annotations'][-1]['description'])
    if m:
        new['start'] = dt_to_tw(adjust_date(new['start'], int(m.group(0))))
        new['annotations'] = new['annotations'][:-1]
        if not new['annotations']:
            del new['annotations']
        print("Timelog: Started task %s minutes ago." % m.group(0))
        
        if tw_to_dt(new['start']) < tw_to_dt(new['entry']):
            new['entry'] = new['start']

# task stopped
if 'start' in old and not 'start' in new:
    started_utc = tw_to_dt(old['start'])
    started_ts = calendar.timegm(started_utc.timetuple())
    started = datetime.fromtimestamp(started_ts)
    stopped = datetime.now()

    if annotation_added:
        new['annotations'].sort(key=lambda anno: anno['entry'])
        m = re.match('^[0-9]+$', new['annotations'][-1]['description'])
        if m:
            new['annotations'] = new['annotations'][:-1]
            if not new['annotations']:
                del new['annotations']
            stopped = adjust_date(stopped, m.group(0))
            if stopped < started:
                print("ERROR: Stop date -%s minutes would be before the start date!" % m.group(0))
                sys.exit(1)
            print("Timelog: Stopped task %s minutes ago." % m.group(0))
    
    entry = "i " + started.strftime("%Y/%m/%d %H:%M:%S")
    entry += " "
    entry += new['project'].replace('.', ':') if 'project' in new else "no project"
    entry += "  " + new['description'] + "\n"
    entry += "o " + stopped.strftime("%Y/%m/%d %H:%M:%S")
    entry += "  ;"
    entry += " :" + ":".join(new['tags']) + ":" if 'tags' in new else ""
    entry += " uuid: " + new['uuid']
    entry += "\n\n"
    with open(LEDGERFILE, "a") as ledger:
        ledger.write(entry.encode("utf-8"))

print(json.dumps(new))
