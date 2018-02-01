#!/usr/bin/env python
#
# Unwrap the data from the Data API, and make a couple of plots.
# 1) Plot of volume and latency
# 2) Plot of scalability of the current application
#
# Assumes data from the week-long view (i.e., 4-hour chunks of data). If this
# isn't true, the labels will be wrong.
#
# Try running it like this:
#     API_KEY=YOUR_API_KEY
#     curl "https://api.tracelytics.com/api-v1/latency/Default/server/series?key=$API_KEY&time_window=week" | python extract.py
import sys
import simplejson as json
from pylab import *
from datetime import datetime

def main():
    data = ''.join(sys.stdin.readlines())
    rows = [r for r in json.loads(data)['data'] if r[2]] # Only plot valid data
    columns = transpose(rows)

    # Format
    dates = [datetime.utcfromtimestamp(v) for v in columns[0]]
    traffic = [v / 4 for v in columns[1]]
    times = [v / 1000 for v in columns[2]]

    # Latency and Volume
    figure()
    subplot(2, 1, 1)
    plot(dates, traffic)
    title('Volume (# of requests)')
    subplot(2, 1, 2)
    plot(dates, times)
    title('Latency (ms)')

    # Latency vs. Volume
    figure()
    plot(traffic, times, '*')
    title('Capacity')
    xlabel('Volume (# of requests / hour)')
    ylabel('Latency (ms)')

    # Display all
    show()

if __name__ == '__main__':
    main()
