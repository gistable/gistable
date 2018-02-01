#!/usr/bin/env python
from __future__ import division

"""
Installation
============

$ curl -O https://gist.githubusercontent.com/wolever/2a15db70f8cb255d753b2cdbb8a718ce/raw/git-work-life
$ chmod +x git-work-life
$ sudo mv git-work-life /usr/local/bin

Usage
=====

$ cd my-git-repo/
$ git work-life *@wolever.net
Summary
-------
4,484 commits
1,364 day span (between 2013-07-17 and 2017-04-11)
891 distinct days (473 days without commits: 34.7%, or ~2.43 days/week)

Day of Week
-----------
Mon: 850 ======================================================================
Tue: 875 ========================================================================
Wed: 814 ===================================================================
Thu: 816 ===================================================================
Fri: 731 ============================================================
Sat: 175 ============
Sun: 223 ================

Hour of Day
-----------
00h: 132 ===========
01h: 123 ==========
02h: 74 ======
03h: 28 =
04h: 20 
05h: 8 
06h: 1 
07h: 6 
08h: 4 
09h: 9 
10h: 50 ===
11h: 89 ========
12h: 170 ===============
13h: 249 ========================
14h: 314 ===============================
15h: 380 ======================================
16h: 475 ================================================
17h: 559 =========================================================
18h: 539 =======================================================
19h: 450 =============================================
20h: 292 ============================
21h: 214 ====================
22h: 154 ==============
23h: 144 ============

Year and Month
--------------
2013-08: 109 ============================
2013-09: 199 ======================================================
2013-10: 191 ====================================================
2013-11: 143 ======================================
2013-12: 179 ================================================
2014-01: 201 =======================================================
2014-02: 153 =========================================
2014-03: 184 ==================================================
2014-04: 135 ====================================
2014-05: 140 =====================================
2014-06: 120 ===============================
2014-07: 92 ========================
2014-08: 57 ==============
"""

import sys
import locale
import subprocess as sp
from fnmatch import fnmatch
from datetime import datetime
from collections import defaultdict

locale.setlocale(locale.LC_ALL, "en_US")

if "-h" in sys.argv or "--help" in sys.argv:
    print "USAGE: %s [AUTHOR_EMAIL_FILTER ...]" %(sys.argv[0], )
    print "For example:"
    print "    $ %s *@wolever.net wolever@akindi.com" %(sys.argv[0], )
    sys.exit(1)


def intcomma(x):
    return locale.format("%d", x, grouping=True)

def make_author_match_func(filters):
    if not filters:
        return None

    def author_match_func(author):
        for filter in filters:
            if author == filter or fnmatch(author, filter):
                return True
        return False

    return author_match_func

def itercommits():
    p = sp.Popen(["git", "log", "--pretty=%ae %aI"], stdout=sp.PIPE)
    while True:
        line = p.stdout.readline()
        if not line:
            break
        author, date_str = line.strip().split()
        # david@wolever.net 2017-04-10T17:50:07-04:00
        tz = date_str[-6:]
        if tz[0] not in "-+":
            raise AssertionError("unexpected date: %r" %(date_str, ))
        date = datetime.strptime(date_str[:-6], "%Y-%m-%dT%H:%M:%S")
        yield (author, date)
    if p.wait() > 0:
        sys.exit(p.wait())

def histogram(f, commits, range=None):
    res = defaultdict(int)
    if range is not None:
        res.update((x, 0) for x in range)
    for commit in commits:
        res[f(commit)] += 1
    return zip(*sorted(res.items()))

def show_histogram(title, histogram, label_format=str, width=60, tick="="):
    minval, maxval = min(histogram[1]), max(histogram[1])
    valspread = maxval - minval
    labels = map(label_format, histogram[0])
    maxlbl = max(map(len, labels))
    print title
    print "-" * len(title)
    for label, count in zip(labels, histogram[1]):
        tick_count = int(0.5 + (
            count if maxval <= width else
            count * (width / valspread)
        ))
        count_str = intcomma(count)
        tick_count = max(0, tick_count - len(count_str))
        print "%*s: %s %s" %(maxlbl, label, count_str, tick_count * tick)


author_match = make_author_match_func(sys.argv[1:])

commits = [
    date for (author, date) in itercommits()
    if author_match is None or author_match(author)
]

if not commits:
    print "No matching commits."
    sys.exit(1)

print "Summary"
print "-------"
print "%s commits" %(intcomma(len(commits)), )
mindate, maxdate = min(commits), max(commits)
total_days = (maxdate - mindate).days
print "%s day span (between %s and %s)" %(
    intcomma(total_days),
    mindate.date().isoformat(),
    maxdate.date().isoformat(),
)
distinct_days = len(set(x.date() for x in commits))
days_off = total_days - distinct_days
time_off_pct = days_off / total_days
print "%s distinct days (%s days without commits: %0.01f%%, or ~%0.02f days/week)" %(
    intcomma(distinct_days),
    days_off,
    time_off_pct * 100,
    time_off_pct * 7,
)
print
show_histogram(
    "Day of Week",
    histogram(lambda x: x.weekday(), commits),
    lambda x: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][x],
)

print
show_histogram(
    "Hour of Day",
    histogram(lambda x: x.hour, commits, range=range(24)),
    lambda x: "%02dh" %(x, ),
)

print
show_histogram(
    "Year and Month",
    histogram(lambda x: (x.year, x.month), commits),
    lambda x: "%s-%02d" %(x[0], x[1]),
)