#!/usr/bin/env python3

# Download https://www.openstack.org/summit/austin-2016/summit-schedule/mine/?goback=1
# to mine.html and then run this script. The my.ics can be imported into your
# calendar.
#
# Common problems:
#   - i've only tested against my calendar (and got feedback about bugs from others) so
#     so you may find the parsing isn't quite right

import datetime
import json
import re

import ics


def fix_json(data):
    # yes, this is terribad
    for line in data.split('\n'):
        line = line.replace('\\', '')  # i just don't care
        match = re.search(r'\s*([\w_]+): (.*)', line)
        if match:
            yield '"{}": {}'.format(*match.groups())
        else:
            yield line


def get_dt(day, time):
    date_template = '2016-04-{:02d} '.format(int(day))
    date = date_template + time + ' -0500'
    return datetime.datetime.strptime(date, '%Y-%m-%d %I:%M%p %z')


calendar = ics.Calendar()
html = open('mine.html', encoding='utf-8').read()
r = r'events\["[^\]0-9]*([0-9]*)"].push\(([^}]+})'
for match in re.finditer(r, html, re.MULTILINE|re.DOTALL):
    day, data = match.groups()
    data = json.loads(''.join(fix_json(data)))

    date_template = '2016-04-{:02d} '.format(int(day))
    begin = get_dt(day, data['start_time'])
    end = get_dt(day, data['end_time'])
    url = ('https://www.openstack.org/summit/austin-2016/'
           'summit-schedule/events/{:d}').format(data['id'])
    location = data['room']

    event = ics.Event(name=data['title'], begin=begin, end=end, #url=url,
                      location=location, description='Details: {}'.format(url))
    event.uid = 'dstanek-{}-event'.format(data['id'])
    calendar.events.append(event)

with open('my.ics', 'w', encoding='utf-8') as f:
    f.writelines(calendar)