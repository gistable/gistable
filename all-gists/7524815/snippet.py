#! /usr/bin/python

#####################
#  GPS-TIME-SYNC    #
#  2013 flazer      #
#  info@flazer.net  #
#####################

# Connects to your GPS-Dongle and synchronize systemtime with GPS-UTC-time.
# Handles local-timezones

import os
import sys
from gps import *
from datetime import datetime
from pytz import timezone

# Change to your timezone:
localzone = 'Europe/Berlin'

print 'Attempting to access GPS...'

try:
  gpsd = gps(mode=WATCH_ENABLE)
except:
  print 'No GPS connection. NO TIME-SYNC.'
  sys.exit()

while True:
  gpsd.next()
  if gpsd.utc != None and gpsd.utc != '':
   tz = timezone('UTC')
   dtz = tz.normalize(tz.localize(datetime(int(gpsd.utc[0:4]), int(gpsd.utc[5:7]), int(gpsd.utc[8:10]), int(gpsd.utc[11:13]), int(gpsd.utc[14:16]), int(gpsd.utc[17:19]))))
   dgmt = dtz.astimezone(timezone(localzone))
   gpstime = dgmt.strftime('%m%d%H%M%Y.%S')
   print 'Synchronizing system time... (' + gpstime + ')'
   os.system('date ' +  gpstime)
   print 'System time set.'
   sys.exit()