#!/usr/bin/python2
# -*- coding: utf-8 -*-

# author: turei.denes@gmail.com

import bs4
import re
import argparse
import os
import sys

def print_message(n, d, m):
    sys.stdout.write('From: %s\nDate: %s\n%s\n\n' % (n, d, m))
    sys.stdout.flush()

parser = argparse.ArgumentParser(description = 
    'Find messages in messages.htm exported from facebook.')
parser.add_argument('--sender', '-s', metavar = 'name', dest = 'name', 
    type = str, nargs = 1,
    help = 'Name (fragment) of the sender',
    required = False)
parser.add_argument('--year', '-y', metavar = 'year', dest = 'year', 
    type = int, nargs = 1, 
    help = 'Year the message was sent',
    required = False)
parser.add_argument('--month', '-m', metavar = 'month', dest = 'month', 
    type = str, nargs = 1,
    help = 'Month the message was sent (e.g. February)',
    required = False)
parser.add_argument('--day', '-d', metavar = 'day', dest = 'day', 
    type = int, nargs = 1,
    help = 'Day (e.g. 23)', required = False)
parser.add_argument('--keywords', '-k', metavar = 'keywords', dest = 'kws', 
    type = str, nargs = '*',
    help = 'Keywords (text fragments) from the message',
    required = False)
parser.add_argument('--file', '-f', metavar = 'path', dest = 'fname', 
    type = str, nargs = 1,
    help = 'Path to messages.htm', required = False)

args = parser.parse_args()

fname = args.fname[0] if args.fname is not None else 'messages.htm'

try:
    redate = re.compile(r'.*(%s %s, %s).*' % \
        (args.month[0].decode('utf-8').capitalize() \
            if args.month is not None else r'[A-Z][a-z]+',
        str(args.day[0]) if args.day is not None else r'[0-9]{1,2}',
        str(args.year[0]) if args.year is not None else r'[0-9]{4}'))
except:
    sys.exit('Invalid date options.')

if not os.path.exists(fname):
    sys.exit('File not found.')

with open(fname, 'r') as f:
        raw = f.read()

try:
    soup = bs4.BeautifulSoup(raw)
except:
    sys.exit('Could not parse html.')

del raw

filtered = [
    (
        span.text,
        span.parent.find_all('span')[1].text,
        span.parent.parent.next_sibling.text
    )
    for span in soup.find_all('span') \
        if 'user' in span['class'] and \
            redate.match(span.parent.find_all('span')[1].text) is not None and \
            (args.name[0] is None or args.name[0].decode('utf-8').lower() \
                in span.text.lower()) and \
            (args.kws is None or \
            len([1 for kw in args.kws \
                if kw.decode('utf-8').lower() in \
                    span.parent.parent.next_sibling.text.lower()]) > 0)
]

sys.stdout.write('%u messages matched.\n\n' % len(filtered))
sys.stdout.flush()

[print_message(*i) for i in reversed(filtered)]