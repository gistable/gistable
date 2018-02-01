#!/usr/bin/env python
# coding: utf-8

"""myprofiler - Casual MySQL Profiler

https://github.com/methane/myprofiler
"""

import os
import sys
import re
from time import sleep
from collections import defaultdict
from ConfigParser import SafeConfigParser
from optparse import OptionParser

try:
    import MySQLdb  # MySQL-python
except ImportError:
    try:
        import pymysql as MySQLdb  # PyMySQL
    except ImportError:
        print "Please install MySQLdb or PyMySQL"
        sys.exit(1)


CMD_PROCESSLIST = "show full processlist"


def connect(conf='~/.my.cnf', section='DEFAULT'):
    """
    connect to MySQL from conf file.
    """
    parser = SafeConfigParser()
    parser.read([os.path.expanduser(conf)])

    host = parser.get(section, 'host')
    user = parser.get(section, 'user')
    password = parser.get(section, 'password')
    if parser.has_option(section, 'port'):
        return MySQLdb.connect(host=host, user=user, passwd=password, port=port)
    else:
        return MySQLdb.connect(host=host, user=user, passwd=password)


def processlist(con):
    con.query(CMD_PROCESSLIST)
    for row in con.store_result().fetch_row(maxrows=200, how=1):
        if row['Info']:
            yield row['Info']


def normalize_query(row):
    """
    Modify query to summarize.
    """
    row = ' '.join(row.split())
    subs = [
            (r"\b\d+\b", "N"),
            (r"\b0x[0-9A-Fa-f]+\b", "0xN"),
            (r"(\\')", ''),
            (r'(\\")', ''),
            (r"'[^']+'", "'S'"),
            (r'"[^"]+"', '"S"'),
            (r'(([NS],){4,})', r'...'),
            ]
    for pat,sub in subs:
        row = re.sub(pat, sub, row)
    return row


def build_option_parser():
    parser = OptionParser()
    parser.add_option(
            '-o', '--out',
            help="write raw queries to this file.",
            )
    parser.add_option(
            '-c', '--config',
            help="read MySQL configuration from. (default: '~/.my.cnf'",
            default='~/.my.cnf'
            )
    parser.add_option(
            '-s', '--section',
            help="read MySQL configuration from this section. (default: '[DEFAULT]')",
            default="DEFAULT"
            )
    parser.add_option(
            '-n', '--num-summary', metavar="K",
            help="show most K common queries. (default: 10)",
            type="int", default=10
            )
    parser.add_option(
            '-i', '--interval',
            help="Interval of executing show processlist [sec] (default: 1.0)",
            type="float", default=1.0
            )
    return parser


def show_summary(counter, limit, file=sys.stdout):
    print >>file, '---'
    items = counter.items()
    items.sort(key=lambda x: x[1], reverse=True)
    for query, count in items[:limit]:
        print >>file, "%4d %s" % (count, query)


def main():
    parser = build_option_parser()
    opts, args = parser.parse_args()

    try:
        outfile = None
        if opts.out:
            outfile = open(opts.out, "w")
        con = connect(opts.config, opts.section)
    except Exception, e:
        parser.error(e)

    counter = defaultdict(int)
    try:
        while True:
            for row in processlist(con):
                if row == CMD_PROCESSLIST:
                    continue
                counter[normalize_query(row)] += 1
                if outfile:
                    print >>outfile, row

            show_summary(counter, opts.num_summary)
            print
            sleep(opts.interval)
    finally:
        if outfile:
            print >>outfile, "\nSummary"
            show_summary(counter, opts.num_summary, outfile)


if __name__ == '__main__':
    main()
