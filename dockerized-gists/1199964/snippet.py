#
# This piece of code is in the public domain.
# <zh.jesse@gmail.com>
#
from datetime import datetime

def get_age(date):
    '''Take a datetime and return its "age" as a string.

    The age can be in second, minute, hour, day, month or year. Only the
    biggest unit is considered, e.g. if it's 2 days and 3 hours, "2 days" will
    be returned.

    Make sure date is not in the future, or else it won't work.
    '''

    def formatn(n, s):
        '''Add "s" if it's plural'''

        if n == 1:
            return "1 %s" % s
        elif n > 1:
            return "%d %ss" % (n, s)

    def q_n_r(a, b):
        '''Return quotient and remaining'''

        return a / b, a % b

    class PrettyDelta:
        def __init__(self, dt):
            now = datetime.now()
            delta = now - dt
            self.day = delta.days
            self.second = delta.seconds

            self.year, self.day = q_n_r(self.day, 365)
            self.month, self.day = q_n_r(self.day, 30)
            self.hour, self.second = q_n_r(self.second, 3600)
            self.minute, self.second = q_n_r(self.second, 60)

        def format(self):
            for period in ['year', 'month', 'day', 'hour', 'minute', 'second']:
                n = getattr(self, period)
                if n > 0:
                    return formatn(n, period)
            return "0 second"

    return PrettyDelta(date).format()

# examples
# get_age(datetime.now()) -> "0 second"
# get_age(datetime(2001, 9, 1)) -> "10 years"
# get_age(datetime(2011, 9, 1)) -> "6 days"