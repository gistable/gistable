#
# Create an ICS calendar with the sessions available at a DC Leisure Centre
#     using the info found by scraping the timetable website
# 
#    http://dalelane.co.uk/blog/?p=3017 
# 
#    Dale Lane
#       dale.lane@gmail.com
#

from bs4 import BeautifulSoup
from dateutil import parser
import urllib, urlparse
import datetime, time
import icalendar
import os


# 
# CONSTANTS
# 
WEBSITEURL = "http://www.dcleisurecentres.co.uk/centres/fleming-park-leisure-centre/timetables/swim"
WEBSITENAME = "Fleming Park"
OUTPUT = "swimflemingpark.ics"


#
# get the date for the day with the provided name
#  (assuming that it's either today or within a week)
# 
def get_next_weekday(now, dayname):
    # convert the day name to a number
    weekday = time.strptime(dayname, "%A").tm_wday
    days_ahead = weekday - now.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return now + datetime.timedelta(days_ahead)

#
# download the schedule from the provided URL
#   parse the contents, and return an array of items containing
#   the sessions described on the page
#
def get_schedule(timetableurl, timetableday):
    # download the page 
    pagecontents = urllib.urlopen(timetableurl).read()
    # parse the page
    soup = BeautifulSoup(pagecontents)

    schedule = []

    # get the first timetable from the page (ignore the other timetables such 
    #  as the timetable for the Teaching Pool)
    timetables = soup.body.find_all("div", class_="timeTable", limit=1)
    for timetable in timetables:
        timetablerows = timetable.find_all("tr")        
        for timetablerow in timetablerows:
            timetableInfo = timetablerow.find_all("td")
            if len(timetableInfo) > 0:
                sessionTime = timetableInfo[0].string
                sessionType = timetableInfo[1].string

                sessionTimes = sessionTime.split(" - ")
                sessionStart = datetime.datetime.combine(timetableday, parser.parse(sessionTimes[0]).time())
                sessionFinish = datetime.datetime.combine(timetableday, parser.parse(sessionTimes[1]).time())

                schedule.append({ 
                    "type" : sessionType, 
                    "start" : sessionStart, 
                    "end" : sessionFinish
                })

    return schedule 

#
# download the page from the provided URL
#   parse the contents, and find the navigation bar containing links 
#   to the schedule for each day of the week
#   return the links, with the dates each link is for
#
def get_days(basetimetableurl):
    now = datetime.datetime.now()

    pagecontents = urllib.urlopen(basetimetableurl).read()
    soup = BeautifulSoup(pagecontents)

    timetables = []

    weekNavMenus = soup.body.find_next("div", class_="ttNavSubDays")
    weekMenu = weekNavMenus.find_all("li")
    for day in weekMenu:
        link = day.find_all("a")
        if link:
            timetables.append({
                "url" : urlparse.urljoin(basetimetableurl, link[0].get('href')), 
                "day" : get_next_weekday(now, link[0].string)
            })

    return timetables


#
# 
#


# timestamp to give to the generated ICS file
scriptruntime = datetime.datetime.now()

# create the new icalendar
cal = icalendar.Calendar()
cal.add("prodid", "-//Swimming Timetable//" + WEBSITENAME + "//")
cal.add("version", "2.0")

# get the list of timetables to download and parse - one for each day
timetables = get_days(WEBSITEURL)

# for each timetable...
for timetable in timetables:
    # download and parse the timetable and get the session info
    for timetableinfo in get_schedule(timetable['url'], timetable['day']):
        # create an event to represent the session 
        event = icalendar.Event()
        event.add("summary", timetableinfo['type'])
        event.add("dtstart", timetableinfo['start'])
        event.add("dtend", timetableinfo['end'])
        event.add("dtstamp", scriptruntime)
        # add the event to the calendar
        cal.add_component(event)

# write the calendar to an ics file
f = open(OUTPUT, 'wb')
f.write(cal.to_ical())
f.close()

