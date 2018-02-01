import datetime

def Easter(year):
    
    """
    Gregorian Calendar
    http://en.wikipedia.org/wiki/Computus
    """

    a = year % 19
    b = int(year / 100)
    c = year % 100
    d = int(b / 4)
    e = b % 4
    f = int((b + 8) / 25)
    g = int((b - f + 1) / 3)
    h = (19*a + b - d - g + 15) % 30
    i = int(c / 4)
    k = c % 4
    L = (32 + 2*e + 2*i - h - k) % 7
    m = int((a + 11*h + 22*L) / 451)
    month = int((h + L - 7*m + 114) / 31)
    day = ((h + L - 7*m + 114) % 31) + 1
    
    return datetime.date(year, month, day)

def GoodFriday(year):

    """Good Friday"""
    
    day = Easter(year)
    while day.weekday() != 4:
        day -= datetime.timedelta(days=1)
    return day

def NewYears(year):

    """New Year's Day"""
    
    day = datetime.date(year, 1, 1)
    if day.weekday() == 5:
        return day + datetime.timedelta(days=2)
    if day.weekday() == 6:
        return day + datetime.timedelta(days=1)
    return day

def MLK(year):

    """Martin Luther King Day"""

    day = datetime.date(year, 1, 1)
    count = 0
    while True:
        if day.weekday() == 0:
            count += 1
            if count == 3:
                return day
        day += datetime.timedelta(days=1)

def PresidentsDay(year):

    """President's Day"""

    day = datetime.date(year, 2, 1)
    count = 0
    while True:
        if day.weekday() == 0:
            count += 1
            if count == 3:
                return day
        day += datetime.timedelta(days=1)

def MayDay(year):

    """Early May Banking Holiday"""

    day = datetime.date(year, 5, 1)
    count = 0
    while True:
        if day.weekday() == 0:
            count += 1
            if count == 1:
                return day
        day += datetime.timedelta(days=1)

def EarlyMayBankHoliday(year):

    """Early May Banking Holiday (UK) : 4th Monday after May Day"""

    day = MayDay(year)
    count = 0
    while True:
        if day.weekday() == 0:
            count += 1
            if count == 4:
                return day
        day += datetime.timedelta(days=1)

def MemorialDay(year):

    """Memorial Day"""

    day = datetime.date(year, 6, 1) - datetime.timedelta(days=1)
    count = 0
    while True:
        if day.weekday() == 0:
            count += 1
            if count == 1:
                return day
        day -= datetime.timedelta(days=1)

def IndependenceDay(year):

    """Independence Day"""

    day = datetime.date(year, 7, 4)
    if day.weekday() == 5:
        return day + datetime.timedelta(days=2)
    if day.weekday() == 6:
        return day + datetime.timedelta(days=1)
    return day

def LaborDay(year):

    """Labor Day"""

    day = datetime.date(year, 9, 1)
    count = 0
    while True:
        if day.weekday() == 0:
            count += 1
            if count == 1:
                return day
        day += datetime.timedelta(days=1)

def ColumbusDay(year):

    """Columbus Day"""

    day = datetime.date(year, 10, 1)
    count = 0
    while True:
        if day.weekday() == 0:
            count += 1
            if count == 2:
                return day
        day += datetime.timedelta(days=1)

def VeteransDay(year):

    """Veterans Day"""

    day = datetime.date(year, 11, 11)
    if day.weekday() == 5:
        return day - datetime.timedelta(days=1)
    if day.weekday() == 6:
        return day + datetime.timedelta(days=1)
    return day

def ThanksgivingDay(year):

    """Thanksgiving Day"""

    day = datetime.date(year, 11, 1)
    count = 0
    while True:
        if day.weekday() == 3:
            count += 1
            if count == 4:
                return day
        day += datetime.timedelta(days=1)

def ChristmasDay(year):

    """Christmas Day"""

    day = datetime.date(year, 12, 25)
    if day.weekday() == 5:
        return day + datetime.timedelta(days=2)
    if day.weekday() == 6:
        return day + datetime.timedelta(days=1)
    return day

def BoxingDay(year):

    """Boxing Day"""
    
    day = datetime.date(year, 12, 26)
    if day.weekday() == 5:
        return day + datetime.timedelta(days=2)
    if day.weekday() == 6:
        return day + datetime.timedelta(days=1)
    return day


def Holidays(year):

    """Get all the Holidays for a given year"""

    holidays = [Easter(year),
                GoodFriday(year),
                NewYears(year),
                MLK(year),
                PresidentsDay(year),
                MayDay(year),
                EarlyMayBankHoliday(year),
                MemorialDay(year),
                IndependenceDay(year),
                LaborDay(year),
                ColumbusDay(year),
                VeteransDay(year),
                ThanksgivingDay(year),
                ChristmasDay(year),
                BoxingDay(year)
                ]

    holidays = dict([(day, 1) for day in holidays]).keys()
    holidays.sort()
    return holidays

if __name__ == '__main__':

	print Holidays(datetime.datetime.now().year)
