#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Convert Combined Log Format stream into TSV file.

To get known about access log, see Apache HTTP server official document.

* [`en <http://httpd.apache.org/docs/2.4/en/logs.html>`_]
* [`ja <http://httpd.apache.org/docs/2.4/ja/logs.html>`_]

Basic usage to parse single access log file is ::

    $ ./combined2tsv.py access.log > access.tsv

``-o/--output`` option is available to specify output file. ::

    $ ./combined2tsv.py access.log -o access.tsv

Multiple input files are acceptable, and gzip format is also okay. ::

    $ ./combined2tsv.py access.log access.log.gz

You can feed standard input using pipe command. ::

    $ head access.log | ./combined2tsv.py

If you want header line, use ``--header`` option. ::

    $ grep "favicon.ico" access.log | ./combined2tsv.py --header

Or if you prefer LTSV format, ``--ltsv`` option is available. ::

    $ tail access.log | ./combined2tsv.py --ltsv

Note that ``--ltsv`` and ``--header`` are mutually exclusive.

Output fields are also changable if you define JSON Table Shema file. ::

    $ head access.log | ./combined2tsv.py -c schema.json

Example shema file looks like::

    {
      "fields": [
        {"id": "time", "type": "datetime", "format": "%Y-%m-%dT%H:%M:%S"},
        {"id": "path", "type": "string"},
        {"id": "query", "type": "string"},
        {"id": "status", "type": "integer"}
      ]
    }
"""

import argparse
import csv
import datetime
import logging
import gzip
import json
import os
import re
import sys
from collections import namedtuple

if sys.version_info[0] == 3:
    imap = map
else:
    from itertools import imap

ENCODING = 'utf-8'
FIELDS = (
    {"id": "time", "type": "datetime", "format": "%Y-%m-%dT%H:%M:%S"},
    {"id": "host", "type": "string"},
    # {"id": "req", "type": "string"},
    {"id": "path", "type": "string"},
    {"id": "query", "type": "string"},
    {"id": "method", "type": "string"},
    {"id": "protocol", "type": "string"},
    {"id": "status", "type": "integer"},
    {"id": "size", "type": "integer"},
    {"id": "referer", "type": "string"},
    {"id": "ua", "type": "string"},
    {"id": "reqtime_microsec", "type": "integer"},
    {"id": "trailing", "type": "string"},
    {"id": "source", "type": "string"}
)

# since `strptime()` is too slow, parse on regex matching.
MONTH_ABBR = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}

# Probably default access log format for IPv4
LOG_FORMAT = re.compile(r"""^
    (?P<host>\S+)\s(?P<ident>\S+)\s(?P<user>\S+)\s
    \[(?P<day>\d{2})/(?P<month>[A-Z][a-z]{2})/(?P<year>\d{4}):
      (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})\s
      (?P<timezone>[+-]\d{4})\]\s
    "(?P<method>[A-Z]+)?\s?(?P<path>[^?^ ]+)?\??(?P<query>\S+)?\s?
     (?P<protocol>HTTP/\d\.\d)?"\s
    (?P<status>\d{3})\s(?P<size>\d+|-)\s"(?P<referer>[^"]+)"\s"(?P<ua>[^"]*)"
    (?P<trailing>.*)
$""", re.VERBOSE)

Access = namedtuple('Access',
    '''host ident user day month year hour minute second timezone
    method path query protocol status size referer ua trailing''')


def parse(raw):
    """ Parse accesslog line to map Python dictionary.

    Returned dictionary has following keys:

    - time: access time (datetime)
    - host: remote IP address.
    - path: HTTP request path, this will be splitted from query.
    - query: HTTP requert query string removed from "?".
    - method: HTTP request method.
    - protocol: HTTP request version.
    - status: HTTP response status code. (int)
    - size: HTTP response size, if available. (int)
    - referer: Referer header. if "-" is given, that will be ignored.
    - ua: User agent. if "-" is given, that will be ignored.
    - ident: remote logname
    - user: remote user
    - trailing: Additional information if using custom log format.

    :param access: internal object which represent accesslog record
    :type access: Access
    :rtype: dict
    """
    m = LOG_FORMAT.match(raw.rstrip())
    if m is None:
        return
    access = Access._make(m.groups())
    entry = {
        'host': access.host,
        'path': access.path,
        'query': access.query,
        'method': access.method,
        'protocol': access.protocol,
        'status': int(access.status)
    }
    entry['time'] = datetime.datetime(
        int(access.year), MONTH_ABBR[access.month], int(access.day),
        int(access.hour), int(access.minute), int(access.second))
    if access.ident != '-':
        entry['ident'] = access.ident
    if access.user != '-':
        entry['user'] = access.user
    if access.size != '-':
        entry['size'] = int(access.size)
    if access.referer != '-':
        entry['referer'] = access.referer
    if access.ua != '-':
        entry['ua'] = access.ua
    if access.trailing:
        entry['trailing'] = access.trailing.strip()
    return entry


class Combined2Tsv(object):

    def __init__(self, header, output=None, callback=None, ltsv=False):
        self.header = header
        self.writer = csv.writer(output or sys.stdout, delimiter='\t',
            quotechar='\t', quoting=csv.QUOTE_NONE)
        self.callback = callback
        self.ltsv = ltsv

    def write_header(self):
        out = map(lambda h: h['id'], self.header)
        self.writer.writerow(out)

    def write(self, dt):
        out = []
        for h in self.header:
            k, t = h['id'], h['type']
            v = dt.get(k, h.get('default'))
            if not v:
                val = ''
            elif t == 'datetime':
                val = v.strftime(h['format'])
            elif t in ('integer', 'float', 'boolean'):
                val = str(v)
            else:
                val = v
            if self.ltsv and v:
                val = k + ':' + val
            out.append(val)
        self.writer.writerow(out)

    def consume(self, stream, source=None):

        def cb(e):
            if source:
                e['source'] = source
            if self.callback:
                self.callback(e)
            self.write(e)

        for line in imap(lambda l: l.rstrip(), stream):
            e = parse(line)
            if e:
                cb(e)
            else:
                logging.error('Fail to parse: %s', line)


def header_parse(entry):
    if not 'trailing' in entry:  # Custome header parsing logic
        return
    for n in entry['trailing'].split():
        kv = n.strip('"').split('=')
        if len(kv) == 2:
            if kv[0] == 'rsptm':
                entry['reqtime_microsec'] = int(kv[1])
            else:
                entry[kv[0]] = kv[1]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-o", "--output", dest="output",
        type=argparse.FileType('w'), metavar="FILE", help="output file")
    parser.add_argument("-c", "--config", type=argparse.FileType('r'),
        help="output schema definition file")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--header",
        action='store_true', help="add header")
    group.add_argument("--ltsv",
        action='store_true', help="make output LTSV format")

    parser.add_argument("files", metavar="FILE", type=argparse.FileType('r'),
        nargs='*', help='accesslog files, gzip is also acceptable')
    try:
        args = parser.parse_args()
    except IOError:
        e = sys.exc_info()[1]
        parser.error("File not found: %s" % (e, ))

    if args.config:
        fields = json.load(args.config)['fields']
        args.config.close()
    else:
        fields = FIELDS

    converter = Combined2Tsv(fields, args.output, header_parse, args.ltsv)
    if args.header:
        converter.write_header()
    if args.files:
        for fp in args.files:
            _, suffix = os.path.splitext(fp.name)
            if suffix == '.gz':
                stream = imap(lambda s: s.decode(ENCODING), gzip.open(fp.name))
            else:
                stream = fp
            converter.consume(stream, os.path.basename(fp.name))
            fp.close()
    else:
        # XXX: flush in some interval to work with `tail -f` command.
        converter.consume(sys.stdin)


def test_accesslog_regex():
    TESTS = '''
127.0.0.1 - - [22/Aug/2011:10:02:03 +0900] "GET / HTTP/1.1" 200 151 "-" "Mozilla/5.0 (Windows NT 5.1; rv:6.0) Gecko/20100101 Firefox/6.0"
127.0.0.1 - - [22/Aug/2011:10:02:03 +0900] "GET /favicon.ico HTTP/1.1" 404 168 "-" "Mozilla/5.0 (Windows NT 5.1; rv:6.0) Gecko/20100101 Firefox/6.0"
127.0.0.1 - - [14/Feb/2012:09:45:28 +0900] "GET /favicon.ico HTTP/1.1" 404 168 "-" ""
127.0.0.1 - - [14/Feb/2012:11:39:50 +0900] "-" 400 0 "-" "-"
127.0.0.1 - firstuser [11/Apr/2012:11:04:52 +0900] "GET /simple/ HTTP/1.1" 200 46 "-" "Python-urllib/2.7"
'''.strip().split('\n')
    error = []
    for t in TESTS:
        e = parse(t)
        if e is None:
            error.append(t)
    if error:
        print('Failed inputs:\n')
        print('\t', '\n\t'.join(error))
        assert False, "see above outputs"


def test_tsv_writer():
    from cStringIO import StringIO
    io = StringIO()
    converter = Combined2Tsv(FIELDS, io)

    # Header output
    converter.write(FIELDS)
    ret = io.getvalue().split('\t')
    assert len(ret) == len(FIELDS), ret
    io.truncate(0)

    # null output
    converter.write({})
    ret = io.getvalue().split('\t')
    assert len(ret) == len(FIELDS), ret
    io.truncate(0)

    # valid output
    converter.write({
        'time': datetime.datetime.now(), 'host': '',
        'path': '', 'query': '',
        'method': '', 'protocol': '',
        'status': 200, 'size': 123,
        'referer': '', 'ua': '',
        'ident': '', 'user': '', 'trailing': ''
    })
    ret = io.getvalue().split('\t')
    assert len(ret) == len(FIELDS), ret
    io.truncate(0)


if __name__ == '__main__':
    main()

# vim: set et ts=4 sw=4 cindent fileencoding=utf-8 :
