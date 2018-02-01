from datetime import date, datetime, timedelta
from icalendar import Calendar, Event
import tempfile, os, pytz

# DEFINITION ####################
class SymphonySchedule:
    def __init__(self, name, deadline, schedule_events=[]):
        self.name = name
        self.deadline = deadline
        self.schedule_events = schedule_events


    def get_schedule_dates(self):
        return { e.name : self.deadline - e.offset for e in self.schedule_events }


    def generate_calendar(self):
        # so we make a calendar to which we add all the events
        cal = Calendar()
        cal['summary'] = self.name
        
        # adds a new event to the calendar for each date in the list
        for event_name, event_date in self.get_schedule_dates().items():
            event = Event()
            event.add('summary', event_name)
            event.add('dtstart', event_date)
            cal.add_component(event)

        # makes a temporary file to export the calendar to
        directory = tempfile.mkdtemp()
        f = open(os.path.join(directory, 'milestones.ics'), 'wb')
        f.write(cal.to_ical())
        f.close()

        # prints the location of the ics file
        print("Generated new calendar for " + self.name + " in this directory:")
        print(directory)


class ScheduleEvent:
    def __init__(self, name, offset):
        self.name = name
        self.offset = offset


# IMPLEMENTATION ####################
tz = pytz.timezone('US/Central')
pats_party_deadline = datetime(2017, 2, 4, 19, 0, 0, tzinfo=tz)

pats_schedule_events = [
    ScheduleEvent("Invitations Due", timedelta(days=28)),
    ScheduleEvent("Purchases Complete", timedelta(days=14)),
    ScheduleEvent("Preparations Complete", timedelta(days=7)),
    ScheduleEvent("Final Arrangements", timedelta(hours=4))
    ]

schedule_symphony = SymphonySchedule("Pat's Party Symphony", pats_party_deadline, pats_schedule_events)
schedule_symphony.generate_calendar()
