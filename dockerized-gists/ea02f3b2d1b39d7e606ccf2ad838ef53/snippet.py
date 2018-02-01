#!/usr/bin/env python3

import csv
import argparse
import statistics
from dateutil import parser, tz
from datetime import datetime, timedelta
from subprocess import call
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as plticker


argparser = argparse.ArgumentParser(description="Plot results")
group = argparser.add_mutually_exclusive_group()
group.add_argument("-u", "--up", action="store_true")
group.add_argument("-d", "--down", action="store_true")
args = argparser.parse_args()

res = call(["scp", "raspi:~/speedtest/reports.txt", "."])

dates = []
download_speeds = []

# fields: Server ID,Sponsor,Server Name,Timestamp,Distance,Ping,Download,Upload
# idx:    0        ,1      ,2          ,3        ,4       ,5   ,6       ,7

prevdate = None
interval = timedelta(minutes=15)
to_zone = tz.tzlocal()


class HFormatter(mdates.DateFormatter):
    def strftime(self, dt, fmt=None):
        if dt.hour % 3 == 0 and dt.hour != 0:
            return super().strftime(dt)
        else:
            return ""

with open('reports.txt') as csvfile:
    data = csv.reader(csvfile)
    for line in data:
        if len(line) == 8:
            prevdate = parser.parse(line[3])
            prevdate.astimezone(to_zone)
            dates.append(prevdate)
            if args.up:
                download_speeds.append(float(line[7]) / 1000000)
            else:
                download_speeds.append(float(line[6]) / 1000000)
        elif prevdate:
            prevdate = prevdate + interval
            dates.append(prevdate)
            download_speeds.append(download_speeds[-1])

days = mdates.DayLocator()
hours = mdates.HourLocator()
d_fmt = mdates.DateFormatter("%a, %-d.%-m %H:%M")
h_fmt = HFormatter("%H:%M")

fig, ax = plt.subplots()
ax.plot(dates, download_speeds)

if args.up:
    ones = plticker.MultipleLocator(base=1.0)
    ax.yaxis.set_major_locator(ones)
else:
    tens = plticker.MultipleLocator(base=10)
    ones = plticker.MultipleLocator(base=2)
    ax.yaxis.set_major_locator(tens)
    ax.yaxis.set_minor_locator(ones)

ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(d_fmt)
ax.xaxis.set_minor_locator(hours)
ax.xaxis.set_minor_formatter(h_fmt)
ax.xaxis.grid(True, which='major')
# ax.yaxis.grid(True, which='major')

# datemin = datetime.date(dates.min().year, 1, 1)
# datemax = datetime.date(dates.max().year + 1, 1, 1)
# ax.set_xlim(datemin, datemax)

fig.autofmt_xdate(rotation=30, which='both')

plt.ylabel("mbit/s")
plt.xlabel("time")
plt.title('%s speed, 15min interval. avg: %.2f; median: %.2f. ' % (('upload' if args.up else 'download'), sum(download_speeds) / len(download_speeds), statistics.median(download_speeds)))
# plt.savefig('%s.png' % (('upload' if args.up else 'download')))
plt.show()
