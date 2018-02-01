""" Make a dictionary that maps timezone abbreviations to timezone names.

The timezone_lookup module supplies a single dictionary, timezone_lookup. For example,

>>> timezone_lookup['EST']
'US/Michigan'
"""

from datetime import datetime
import pytz

timezone_lookup = dict([(pytz.timezone(x).localize(datetime.now()).tzname(), x) for x in pytz.all_timezones])
