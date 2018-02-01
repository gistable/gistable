#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""nginx_error_rate -- Munin plugin to report the error rate in an access log.

The access log defaults to `/var/log/nginx/access.log`. This may be
customized with the following stanza in your munin plugin conf:

[nginx_error_rate]
env.access_log /path/to/access.log
"""
#%# family=auto
#%# capabilities=autoconf

import os
import datetime as dt
import re
from collections import deque, defaultdict


date_cp = re.compile(r'''
\[
  (?P<day>\d+)
  /
  (?P<month>\w+)
  /
  (?P<year>\d+)
  :
  (?P<hour>\d+)
  :
  (?P<minute>\d+)
  :
  (?P<second>\d+)
  \              # Space
  [^\]]+
\]''', re.VERBOSE)
error_cp = re.compile(r' (50[0-5]) ')

month_num = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12,
    }


def main():
    error_lines = deque()
    access_log = os.path.abspath(os.path.expanduser(os.environ.get('access_log', '/var/log/nginx/access.log')))
    if not os.path.exists(access_log):
        return
    
    with open(access_log) as fi:
        for line in fi:
            match = error_cp.search(line)
            if match is not None:
                error_lines.append((match.group(1), line.strip()))

    now = dt.datetime.now()
    d15m = now - dt.timedelta(minutes=15)
    d5m = now - dt.timedelta(minutes=5)
    by_second_15m = defaultdict(lambda: 0)
    by_second_5m = defaultdict(lambda: 0)
    for code, line in reversed(error_lines):
        match = date_cp.search(line)
        if match is not None:
            data = match.groupdict()
            date = dt.datetime(
                int(data['year'], base=10),
                month_num[data['month']],
                int(data['day'], base=10),
                int(data['hour'], base=10),
                int(data['minute'], base=10),
                int(data['second'], base=10),
                )
            if date < d15m:
                break
            by_second_15m[date] += 1
            if date >= d5m:
                by_second_5m[date] += 1

    avg_15m = sum(by_second_15m.itervalues()) / 900.0 if by_second_15m else 0.0
    avg_5m = sum(by_second_5m.itervalues()) / 300.0 if by_second_5m else 0.0

    print "errors_15m.value", avg_15m
    print "errors_5m.value", avg_5m


def config():
    print "graph_title Nginx error rate"
    print "graph_category nginx"
    print "graph_vlabel Errors per second"
    print "errors_5m.label Errors per second over 5 minutes"
    print "errors_15m.label Errors per second over 15 minutes"


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) > 1:
        parser.error('Too many arguments.')
    elif len(args) < 1:
        main()
    elif args[0] == 'config':
        config()
