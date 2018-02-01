#!/usr/local/bin/python

# a Python script for PyEphem
# http://rhodesmill.org/pyephem/
# to find out the sunrise and sunset time
# in UTC
# (add more code for the local time by yourself)
# by Kenji Rikitake 6-OCT-2009

from datetime import datetime, timedelta
from time import localtime, strftime
import ephem

SEC30 = timedelta(seconds=30)

home = ephem.Observer()
# replace lat, long, and elevation to yours
home.lat = 'YOUR LATITUDE (+:NORTH)'
home.long = 'YOUR LONGITUDE (+:EAST)'
home.elevation = number_in_meter

sun = ephem.Sun()

fmt = "%d-%b-%Y %H%MUTC"

if __name__ == '__main__':

    sun.compute(home)

    nextrise = home.next_rising(sun)
    nextset = home.next_setting(sun)

    nextriseutc= nextrise.datetime() + SEC30
    nextsetutc= nextset.datetime() + SEC30

    print "next sunrise: ", nextriseutc.strftime(fmt)
    print "next sunset:  ", nextsetutc.strftime(fmt)

# end of code
