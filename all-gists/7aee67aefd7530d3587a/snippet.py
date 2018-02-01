#!/usr/bin/env python

# usage ./verify_splunk_coverage.py <log_file>

# set these from splunk-apps/apps/<service-name>/default/props.conf
BREAK_ONLY_BEFORE_REGEX=r'^\d\d:\d\d:\d\d\s\[[^\]]+\]'
EXTRACT_REGEX=r'^\d?\d:\d\d:\d\d\s\[(?P<thread>[^\]]+)\]\s\[(?P<loglevel>\w+)\]\s\[(?P<class>[^\]]+)\]\s\[(?P<username>[^\]]*)\](?P<message>.*)$'

import re,sys
f = open(sys.argv[1])

s = f.readline()
while True:
  n = f.readline()
  if not n:
    if not re.match(EXTRACT_REGEX, s):
       print "Failed to match line " + s
    sys.exit(0)
  if not re.match(BREAK_ONLY_BEFORE_REGEX, n):
    s = s + n
  else:
     if not re.match(EXTRACT_REGEX, s):
       print "Failed to match line:\n", s
     s = n