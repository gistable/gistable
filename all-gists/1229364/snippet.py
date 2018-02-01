""" Generate an iCalendar file from the Frederick County, VA Government
    RSS feed of events.

    Requirements:
        feedparser
        icalendar
"""
from datetime import datetime
import sys

from icalendar import Calendar, Event, LocalTimezone
import feedparser

DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

feed = feedparser.parse("http://www.co.frederick.va.us/fredcocal.xml")

cal = Calendar()
cal.add('VERSION', '2.0')
cal.add('PRODID', 'feed2ical 0.1')
cal.add('X-WR-CALNAME;VALUE=TEXT', feed.channel.title)
cal.add('X-WR-CALDESC;VALUE=TEXT', feed.channel.description)

for item in feed['items']:
    
    event_date = datetime.strptime(
        item.caldate, DATE_FORMAT).replace(tzinfo=LocalTimezone())
    published_date = datetime.strptime(
        item.updated, DATE_FORMAT).replace(tzinfo=LocalTimezone())
    
    event = Event()
    event.add('UID', item.guid)
    event.add('SUMMARY', item.title)
    event.add('DESCRIPTION', item.description)
    event.add('URL;VALUE=URI', item.link)
    event.add('DTSTART', event_date.date())
    event.add('DTEND', event_date.date())
    event.add('DTSTAMP', published_date)
    
    cal.add_component(event)

sys.stdout.write(cal.as_string())