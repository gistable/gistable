#!/usr/bin/env python
#
# Bug Prediction script inspired by:
# http://google-engtools.blogspot.com/2011/12/bug-prediction-at-google.html
# Roman Bogorodskiy <bogorodskiy@gmail.com>
#

from __future__ import print_function

import argparse
import math
import re
import sys
import time
from operator import itemgetter

import git


def calc_score(commit_ts, first_commit_ts, now_ts):
    t = 1 - float(now_ts - commit_ts) / (now_ts - first_commit_ts)
    assert 0 <= t <= 1
    return 1.0 / (1 + math.exp(-12 * t + 12))


def calculate_scores(files, first_commit_ts, now_ts):
    result = {}

    for f in files.iterkeys():
        file_score = 0
        for ts in files[f]:
            file_score += calc_score(ts, first_commit_ts, now_ts)

        result[f] = file_score

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', dest='expr', type=str,
            default="Security:",
            help="Regular expression to search for in commit log")
    parser.add_argument('-l', dest='limit', type=int,
            default=None, help="Number of results to show")
    parser.add_argument('path', type=str, nargs='?',
            default=".", help="Repository path")

    args = parser.parse_args()

    try:
        repo = git.Repo(args.path)
    except git.exc.InvalidGitRepositoryError:
        print("Invalid git repository: %s" % args.path, file=sys.stderr)
        sys.exit(1)

    filter_re = re.compile(args.expr)

    dangerous_files = {}
    commits = matches = 1

    for commit in repo.iter_commits('main'):
        if commits == 1 or commits % 100 == 0:
            print(commits, end='')
        elif commits % 10:
            print(".", end='')

        if filter_re.search(commit.message):
            matches += 1
            for f in commit.stats.files.keys():
                if f not in dangerous_files:
                    dangerous_files[f] = [commit.committed_date, ]
                else:
                    dangerous_files[f].append(commit.committed_date)
        commits += 1
    print(commits)

    first_commit_ts = commit.committed_date

    scores = calculate_scores(dangerous_files,
            first_commit_ts, int(time.time()))

    for i in sorted(scores.items(), key=itemgetter(1),
            reverse=True)[:args.limit]:
        print (i[0], i[1])