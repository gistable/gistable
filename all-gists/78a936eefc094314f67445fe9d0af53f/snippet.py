#!/usr/bin/env python3
# coding=UTF8
# Author: Iñaki Ucar <i.ucar86@gmail.com>
# Description: Download all events, births and deaths from Wikipedia

import sys, requests, locale
from datetime import date, timedelta as td
from pypandoc import convert # <3

MAX_TITLES = 50
API = 'http://en.wikipedia.org/w/api.php'
locale.setlocale(locale.LC_TIME, 'en_US')

def query_content(request):
    request['action'] = 'query'
    request['format'] = 'json'
    request['prop'] = 'revisions'
    request['rvprop'] = 'content'
    request['formatversion'] = 2
    lastContinue = {'continue': ''}
    while True:
        # Clone original request
        req = request.copy()
        # Modify it with the values returned in the 'continue' section of the last result.
        req.update(lastContinue)
        # Call API
        result = requests.get(API, params=req).json()
        if 'error' in result:
            raise Error(result['error'])
        if 'warnings' in result:
            print(result['warnings'])
        if 'query' in result:
            yield result['query']
        if 'continue' not in result:
            break
        lastContinue = result['continue']

def chunks(l, n):
    # Yield successive n-sized chunks from l
    for i in range(0, len(l), n):
        yield l[i:i + n]

d1 = date(2016, 9, 1)
d2 = date(2017, 8, 31)
delta = d2 - d1
days = [(d1 + td(days=i)).strftime('%B_%-d') for i in range(delta.days + 1)]

for chunk in chunks(days, MAX_TITLES):
    for query in query_content({'titles': '|'.join(chunk)}):
        for page in query['pages']:
            day = page['title']
            content = page['revisions'][0]['content']
            content = convert(content, 'plain', format='mediawiki')
            content = content.split('\n\n\n')
            try:
                # in a proper formatting we trust
                start = [i for i, s in enumerate(content) if 'Events' in s][0]
                for i in range(start, start + 3):
                    section = content[i].split('\n\n')
                    title = section[0].replace('\n', '')
                    lines = section[1].replace('\n    ', '')
                    for line in lines.replace('-   ', '').split('\n'):
                        line = line.replace('"', "'")
                        print('{} {} "{}"'.format(day, title, line))
            except Exception as e:
                print(e, file=sys.stderr)
                print(day, file=sys.stderr)
                sys.exit(1)
