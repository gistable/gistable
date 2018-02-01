#!/usr/bin/env python
# coding: utf-8

'''
中国联不通每月通话时间统计
用法：

1. 去 http://iservice.10010.com/ 下载通话详单（Excel 格式），导出为 CSV
2. ./sumup.py *.csv
'''

from collections import defaultdict
from csv import DictReader
from decimal import Decimal
from itertools import chain
import re
import sys

DURATION_PATTERN = re.compile(r'(?:(\d+)小时)?(?:(\d+)分)?(?:(\d+)秒)?')
ID, TIME, DURATION, NUMBER, FEE = range(5)

def extract(row):
    return [row[f] for f in '序号,通话起始时间,通话时长,对方号码,小计'.split(',')]

def to_minutes(s):
    hour, minute, second = DURATION_PATTERN.match(s).groups()
    minute = int(minute) if minute else 0
    if hour:
        minute += int(hour) * 60
    if second:
        minute += 1
    return minute

def load_data(paths):
    calls = defaultdict(list)

    for row in chain.from_iterable(DictReader(open(p)) for p in paths):
        if row['呼叫类型'] != '主叫':
            continue
        row = extract(row)
        calls[row[TIME][:7]].append(row)

    return sorted(calls.iteritems(), key=lambda (k, v): k)

def main():
    calls_by_month = load_data(sys.argv[1:])
    for month, calls in calls_by_month:
        fee = sum(Decimal(c[FEE]) for c in calls)
        minutes = sum(to_minutes(c[DURATION]) for c in calls)
        print '%s: %s minutes - ￥%s' % (month, minutes, fee)

if __name__ == '__main__':
    main()