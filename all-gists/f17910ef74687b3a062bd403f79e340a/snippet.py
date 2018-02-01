import datetime
from dateutil.relativedelta import relativedelta

def today(date=None,iso=False):
    if date is None: date=datetime.date.today()
    if iso: return date.isoformat()
    else: return date

def yesterday(date=None,iso=False):
    if date is None: date=today()
    yesterday = date.today() - relativedelta(days=1)
    if iso: return yesterday.isoformat()
    return yesterday

def tomorrow(date=None,iso=False):
    if date is None: date=today()
    tomorrow=date.today() + relativedelta(days=1)
    if iso: return tomorrow.isoformat()
    return tomorrow

def last_week(date=None,daterange=True,iso=False):
    if date is None: date=today()
    start_date = date + relativedelta(days=-date.weekday(), weeks=-1)
    end_date = start_date + relativedelta(days=6)
    if daterange:
        if iso: return start_date.isoformat(),end_date.isoformat()
        else: return start_date, end_date

def this_week(date=None,daterange=True,iso=False):
    if date is None: date=today()
    start_date = date + relativedelta(days=-date.weekday())
    end_date = start_date + relativedelta(days=6)
    if daterange:
        if iso:
            return start_date.isoformat(), end_date.isoformat()
        else:
            return start_date, end_date
    
def next_week(date=None,daterange=True,iso=False):
    if date is None: date=today()
    start_date = date + relativedelta(days=-date.weekday(), weeks=1)
    end_date = start_date + relativedelta(days=6)
    if daterange:
        if iso:
            return start_date.isoformat(), end_date.isoformat()
        else:
            return start_date, end_date

def later_this_week(date=None,incl=False,daterange=True,iso=False):
    date=today(date)
    start_date, end_date = this_week(date)
    if not incl: start_date=tomorrow(date)
    else: start_date=today(date)
    #Really need to check if today is last day of week?
    if daterange:
        if iso:
            return start_date.isoformat(), end_date.isoformat()
        else:
            return start_date, end_date
        
def earlier_this_week(date=None,incl=False,daterange=True,iso=False):
    date=today(date)
    start_date, end_date = this_week(date)
    if not incl: end_date=yesterday(date)
    else: end_date=today(date)
    #Really need to check if today is first day of week?
    if daterange:
        if iso:
            return start_date.isoformat(), end_date.isoformat()
        else:
            return start_date, end_date
    
def last_month(date=None,daterange=True,iso=False):
    if date is None: date=today()
    end_date = date.replace(day=1)- relativedelta(days=1)
    start_date = end_date.replace(day=1)
    if daterange:
        if iso: return start_date.isoformat(),end_date.isoformat()
        else: return start_date, end_date

def next_month(date=None,daterange=True,iso=False):
    if date is None: date=today()
    end_date = date+ relativedelta(months=2)
    end_date=end_date.replace(day=1)- relativedelta(days=1)
    start_date = end_date.replace(day=1)
    if daterange:
        if iso: return start_date.isoformat(),end_date.isoformat()
        else: return start_date, end_date

def this_month(date=None,daterange=True,iso=False):
    if date is None: date=today()
    end_date = next_month(date)[0]- relativedelta(days=1)
    start_date = end_date.replace(day=1)
    if daterange:
        if iso: return start_date.isoformat(),end_date.isoformat()
        else: return start_date, end_date

def earlier_this_month(date=None,incl=False,daterange=True,iso=False):
    if date is None: date=today()
    start_date, end_date = this_month(date)
    if not incl: end_date=yesterday(date)
    else: end_date=today(date)
    #Really need to check if today is first day of month?
    if daterange:
        if iso:
            return start_date.isoformat(), end_date.isoformat()
        else:
            return start_date, end_date
    
def later_this_month(date=None,incl=False,daterange=True,iso=False):
    if date is None: date=today()
    start_date, end_date = this_month(date)
    if not incl: start_date=tomorrow(date)
    else: start_date=today(date)
    #Really need to check if today is last day of month?
    if daterange:
        if iso:
            return start_date.isoformat(), end_date.isoformat()
        else:
            return start_date, end_date   

#via http://stackoverflow.com/a/2384407/454773
MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
def day_lastweek(day=MON,date=None,iso=False):
    if date is None: date=today()
    qday= last_week()[0] + relativedelta(days=day)
    if iso: return qday.isoformat()
    return qday

def day_thisweek(day=MON,date=None,iso=False):
    if date is None: date=today()
    qday= this_week()[0] + relativedelta(days=day)
    if iso: return qday.isoformat()
    return qday

def day_nextweek(day=MON,date=None,iso=False):
    if date is None: date=today()
    qday= next_week()[0] + relativedelta(days=day)
    if iso: return qday.isoformat()
    return qday