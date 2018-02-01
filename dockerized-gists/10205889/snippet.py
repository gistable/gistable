#!/usr/bin/python
# 
# CSV logging script for stock dump1090
#
# Uses the Requests library to compare the state of planes in view
# and prints changes to standard out
#
# Start dump1090
# modify this script to point to your dump1090 URL if different
# run the script and pipe the output to a file eg:
#
# nohup ./comparer.py >> data.csv 2> data.err < /dev/null &
#
# @th0ma5 on twitter
# http://th0ma5w.github.io
#

import requests, json, datetime, time

get_data = lambda : json.loads(requests.get('http://127.0.0.1:8095/data.json').content)
data_diff = lambda new,old : [x for x in new if x not in old]
make_date = lambda : str(datetime.datetime.now())

old_data = []

while True:
        try:
                new_data = get_data()
                diffs = data_diff(new_data,old_data)
                old_data = new_data
                if len(diffs) > 0:
                        diff_lines = [','.join([str(y).strip() for y in [make_date()] + x.values()]) for x in diffs]
                        for line in diff_lines:
                                print line
        except:
                pass
        time.sleep(0.5)

