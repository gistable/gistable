from icalendar import Calendar
from icalendar.cal import Event
import datetime
import urllib2
import csv
import sys

for url, label in (
        (
            urllib2.urlopen('https://www.google.com/calendar/ical/11111111111111111111111111%40group.calendar.google.com/private-11111111111111111111111111111111/basic.ics'),
            'werk',
        ),
        (
            urllib2.urlopen('https://www.google.com/calendar/ical/11111111111111111111111111%40group.calendar.google.com/private-11111111111111111111111111111111/basic.ics'),
            'vrij',
        ),
    ):
    cal = Calendar.from_ical(url.read())
    rows = []
    for c in cal.walk():
        if isinstance(c, Event):
            dtstart = c['DTSTART'].dt.strftime('%Y-%m-%d %H:%M:%S')
            dtend = c['DTEND'].dt.strftime('%Y-%m-%d %H:%M:%S')
            if c['DTSTART'].dt.year == 2013 and c['DTSTART'].dt.month == int(sys.argv[1]):
                rows.append([dtstart, dtend, c['SUMMARY'], \
                    c['DTEND'].dt - c['DTSTART'].dt])
    with open(label+'.csv', 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['DTSTART', 'DTEND', 'SUMMARY', 'DURATION'])
        for row in rows:
            csvwriter.writerow(row)