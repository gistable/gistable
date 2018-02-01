import jdcal
from jdcal import ipart, fpart, is_leap, gcal2jd, jd2gcal

CJ = 36525.0


def days_in_year(year, c="g"):
    """Number of days in a calendar year (Gregorian/Julian)."""
    if c.lower() == "g":
        return 366 if is_leap(year) else 365
    elif c.lower() == "j":
        return 365
    else:
        raise ValueError("Unknow calendar type %s ." % c)


def gyear2jd(year):
    y = ipart(year)
    d = fpart(year) * days_in_year(y)
    day = ipart(d)
    jd1, jd2 = gcal2jd(y, 1, day)
    jd2 += fpart(d)
    return jd1, jd2


def gyear2gcal(year):
    jd1, jd2 = gyear2jd(year)
    return jd2gcal(jd1, jd2)


def jd2gyear(jd1, jd2):
    y, m, d, f = jd2gcal(jd1, jd2)
    jdt_1, jdt_2 = gcal2jd(y, 1, 0)
    day_diff = (jd1 - jdt_1) + (jd2 - jdt_2)
    return y + (day_diff / days_in_year(y))


def gcal2gyear(y, m, d):
    jd1, jd2 = gcal2jd(y, m, d)
    return jd2gyear(jd1, jd2)


def jepoch2jd(year):
    mjd = MJD_JD2000 + ((year - 2000.0) * (CJ / 100.0))
    return MJD_0, mjd


def jd2jepoch(jd1, jd2):
    dy = ((jd1 - MJD_0) + (jd2 - MJD_JD2000)) * (100.0 / CJ)
    return 2000.0 + dy

