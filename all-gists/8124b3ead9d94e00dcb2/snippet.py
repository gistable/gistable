#!/usr/bin/env python2.7

try:
    import simplejson as json
except ImportError:
    import json

import tempfile
import sqlite3
import subprocess
import sys
import os

def dumps(doc):
    return json.dumps(doc,
                      separators=(',',':'), ##compact the output
                      indent=None,          ##disable whitespace
                      check_circular=False, ##we know these aren't circular
                      )

conn = sqlite3.connect(':memory:')

created = False

with conn:
    # all one transaction

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        fields = line.split('\t')
        fields = map(json.loads, fields)

        if not created:
            conn.execute("CREATE TABLE tbl(%s)"
                         % ','.join(('f%d'%x) for x in range(len(fields))))
            created = True

        conn.execute("INSERT INTO tbl VALUES(%s);" % ','.join(('?',) * len(fields)),
                     fields)

for arg in sys.argv[1:]:
    for line in conn.execute(arg):
        fields = map(dumps, line)

        print '\t'.join(fields)
