######################################################################
#  CURRENT AWARE LOCAL DATETIME
######################################################################

from datetime import datetime
from tzlocal import get_localzone

local_tz = get_localzone()
local_dt = datetime.now(local_tz)

print local_dt

######################################################################
#  CURRENT AWARE DATETIME IN UTC TIMEZONE
######################################################################

import pytz
from datetime import datetime

utc_tz = pytz.timezone('UTC')
utc_dt = datetime.now(utc_tz)

print utc_dt

######################################################################
#  CURRENT AWARE DATETIME IN CHICAGO TIMEZONE
######################################################################

import pytz
from datetime import datetime

chicago_tz = pytz.timezone('America/Chicago')
chicago_dt = datetime.now(chicago_tz)

print chicago_dt

######################################################################
#  CURRENT TIMESTAMP
######################################################################

from time import time

timestamp = int(time())

print timestamp

######################################################################
# TIMESTAMP TO LOCAL AWARE DATETIME
######################################################################

from datetime import datetime
from tzlocal import get_localzone

timestamp = 1367319130

local_tz = get_localzone()
local_dt = local_tz.localize(datetime.fromtimestamp(timestamp))

print local_dt

######################################################################
# TIMESTAMP TO UTC AWARE DATETIME
######################################################################

import pytz
from datetime import datetime

timestamp = 1367319130

utc_tz = pytz.timezone('UTC')
utc_dt = utc_tz.localize(datetime.utcfromtimestamp(timestamp))

print utc_dt 

######################################################################
# TIMESTAMP TO CHICAGO AWARE DATETIME
######################################################################

import pytz
from datetime import datetime

timestamp = 1367319130

utc_tz = pytz.timezone('UTC')
utc_dt = utc_tz.localize(datetime.utcfromtimestamp(timestamp))

chicago_tz = pytz.timezone('America/Chicago')
chicago_dt = chicago_tz.normalize(utc_dt.astimezone(chicago_tz))

print chicago_dt

######################################################################
# AWARE DATETIME TO TIMESTAMP
######################################################################

import pytz
import calendar
from datetime import datetime

chicago_tz = pytz.timezone('America/Chicago')
chicago_dt = chicago_tz.localize(datetime(2013, 4, 30, 5, 52, 10))

timestamp = calendar.timegm(chicago_dt.utctimetuple())

print timestamp

######################################################################
# AWARE DATETIME TIMEZONE CONVERTION
######################################################################

import pytz
from datetime import datetime

chicago_tz = pytz.timezone('America/Chicago')
chicago_dt = chicago_tz.localize(datetime(2013, 4, 30, 5, 52, 10))

sofia_tz = pytz.timezone('Europe/Sofia')
sofia_dt = sofia_tz.normalize(chicago_dt.astimezone(sofia_tz))

print sofia_dt
