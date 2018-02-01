from datetime import date, timedelta
from dateutil import easter
from dateutil.relativedelta import *

def get_holidays(year=2010):
    """ Returns Polish hollidays dates (legally considered non-working days) """
    easter_sunday = easter.easter(year)
    holidays = {'New Year': date(year,1,1),
                'Trzech Kroli': date(year,1,6),
                'Easter Sunday': easter_sunday,
                'Easter Monday': easter_sunday + timedelta(days=1),
                'Labor Day': date(year,5,1),
                'Constitution Day': date(year,5,3),
                # 7th Sunday after Easter
                # (notice days+1 - this is 7th Sunday excluding Easter Sunday
                'Pentecost Sunday': easter_sunday + relativedelta(days=+1, weekday=SU(+7)),
                # 9th Thursday after Easter
                'Corpus Christi': easter_sunday + relativedelta(weekday=TH(+9)),
                'Assumption of the Blessed Virgin Mary': date(year,8,15),
                'All Saints\' Day': date(year,11,1),
                'Independence Day': date(year,11,11),
                'Christmas  Day': date(year, 12, 25),
                'Boxing Day': date(year, 12, 26),
                }
    return holidays

if __name__ == "__main__":
    print get(2010)
