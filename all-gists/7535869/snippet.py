from dateutil import rrule
from datetime import datetime

def get_schedule_holidays_rrules():
    return [
        rrule.rrule(rrule.YEARLY, dtstart=datetime.now(), bymonth=1, bymonthday=1),              # New Years
        rrule.rrule(rrule.YEARLY, dtstart=datetime.now(), bymonth=5, byweekday=rrule.MO(-1)),    # Memorial
        rrule.rrule(rrule.YEARLY, dtstart=datetime.now(), bymonth=7, bymonthday=4),              # Independence
        rrule.rrule(rrule.YEARLY, dtstart=datetime.now(), bymonth=11, byweekday=rrule.TH(4)),    # Thanksgiving
        rrule.rrule(rrule.YEARLY, dtstart=datetime.now(), bymonth=12, bymonthday=25),            # Christmas
    ]