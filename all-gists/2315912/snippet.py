# -*- coding: utf-8 -*-
from datetime import date, timedelta
from calendar import monthrange

__all__ = ['DateEx',]

class DateEx(date):
    """
    >>> d = DateEx(2012, 1, 31)
    >>> d
    DateEx(2012, 1, 31)
    >>> d >> 1
    DateEx(2012, 2, 29)
    >>> d << 1
    DateEx(2011, 12, 31)
    >>> d + 1
    DateEx(2012, 2, 1)
    >>> d - 1
    DateEx(2012, 1, 30)
    >>> d - 1 >> 1
    DateEx(2012, 2, 29)
    >>> d + 1000
    DateEx(2014, 10, 27)
    >>> d.to(d+10)
    <generator object to at ...>
    >>> list(d.to(d+3))
    [DateEx(2012, 1, 31), DateEx(2012, 2, 1), DateEx(2012, 2, 2)]
    """

    @classmethod
    def fromdate(cls, d):
        return cls(d.year, d.month, d.day)

    def __add__(self, num):
        if isinstance(num, int):
            return self.fromdate(self + timedelta(days=num))
        return self.fromdate(date.__add__(self, num))

    def __sub__(self, num):
        return self + (num * -1)

    def __rshift__(self, num):
        y = self.year
        m = self.month
        m += num
        if 1 <= m <= 12:
            pass
        else:
            m -= 1
            y += m / 12
            m = m % 12
            m += 1
        try:
            return self.replace(year=y, month=m)
        except ValueError:
            return self.replace(year=y, month=m, day=monthrange(y,m)[1])

    def __lshift__(self, num):
        return self >> (num * -1)

    def to(self, d):
        for o in range(self.toordinal(), d.toordinal()):
            yield self.fromdate(date.fromordinal(o))
