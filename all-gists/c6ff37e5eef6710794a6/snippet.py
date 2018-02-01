#!/usr/bin/env python
'''Git Statistics'''

import argparse
import sys
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo

class UTC(tzinfo):
    '''UTC tzinfo'''
    def __init__(self):
        '''init'''
        pass
    def utcoffset(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return 'UTC'
    def dst(self, dt):
        return timedelta(0)

def make_date_range(days=30):
    '''make a date range tuple of specified days range from now'''
    return (datetime.now(UTC()) - timedelta(days=days),
            datetime.now(UTC()),)

def stream_source():
    '''yield the stream source'''
    for line in sys.stdin:
        commit = line.strip().split('|')
        yield (commit[0],
               datetime.strptime(commit[1], '%Y-%m-%d %H:%M:%S %z'),
               commit[2],
               commit[3],)

def window(commits, condition):
    '''returns commits passing the condition'''
    for commit in commits:
        if condition(commit):
            yield commit

def uniq_contributor(commits):
    '''returns uniq contributions'''
    def __uniq__(commits):
        '''agregate uniq contributors'''
        contributors = {}
        for commit in commits:
            author = commit[-1]
            if author in contributors:
                contributors[author] += 1
            else:
                contributors[author] = 1
        return contributors
    for author, count in __uniq__(commits).items():
        yield (author, count,)

def window_by_date(args=None):
    '''print the commits in the given date range'''
    date_range = make_date_range(days=args.days)
    date_predicate = lambda c: date_range[0] <= c[1] <= date_range[1]
    for commit in window(stream_source(), date_predicate):
        print(commit)

def uniq_contributors(args=None):
    '''Print uniq contributors for the project or given window'''
    predicate = lambda c: True
    if args.days:
        date_range = make_date_range(days=args.days)
        predicate = lambda c: date_range[0] <= c[1] <= date_range[1]
    for committer in uniq_contributor(window(stream_source(), predicate)):
        print(committer)

def build_argparser():
    '''Parse command line arguments'''
    parser = argparse.ArgumentParser(prog='git_stat')
    sub_parser = parser.add_subparsers()

    date_window_parser = sub_parser.add_parser('window')
    date_window_parser.add_argument(
        '-d', '--days',
        type=int,
        help='Specify, in days, the size of the window',
        dest='days')
    date_window_parser.set_defaults(func=window_by_date)

    uniq_contributors_parser = sub_parser.add_parser('uniq')
    uniq_contributors_parser.add_argument(
        '-w', '--window',
        type=int,
        help='Window; specify, in days, size of window',
        dest='days')
    uniq_contributors_parser.set_defaults(func=uniq_contributors)

    return parser

def main():
    '''Git stat main'''
    args = build_argparser().parse_args(sys.argv[1:])
    args.func(args)

if __name__ == '__main__':
    main()
