#!/usr/bin/env python

from datetime import datetime

import os
import sys
from dateutil.relativedelta import relativedelta
import sh

def checkout_repo_at(path, dt):
    sha = sh.git('rev-list', '-n', '1', '--before="{0}"'.format(dt.isoformat()), 'origin/master', _cwd=path)
    sha = sha.strip()
    sh.git.reset('--hard', sha, _cwd=path)
    return sha


def date_range(start, stop, step):
    accumulator = start
    while accumulator < stop:
        yield accumulator
        accumulator += step


def main():
    start_date = datetime(2012, 1, 1)
    end_date = datetime.today()
    interval = relativedelta(months=1)
    # interval = relativedelta(days=1)


    repo_path = os.getcwd()

    for date in date_range(start=start_date, stop=end_date, step=interval):
        checkout_repo_at(repo_path, dt=date)
        print "> sonar-runner " + '-Dsonar.projectDate={0}'.format(date.date().isoformat())
        sh.sonar_runner('-Dsonar.projectDate={0}'.format(date.date().isoformat()))


if __name__ == '__main__':
    main()
