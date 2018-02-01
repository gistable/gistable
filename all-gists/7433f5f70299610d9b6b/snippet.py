# When you're sure of the format, it's much quicker to explicitly convert your dates than use `parse_dates`
# Makes sense; was just surprised by the time difference.
import pandas as pd
from datetime import datetime
to_datetime = lambda d: datetime.strptime(d, '%m/%d/%Y %H:%M')

%time trips = pd.read_csv('data/divvy/Divvy_Trips_2013.csv', parse_dates=['starttime', 'stoptime'])
# CPU times: user 1min 29s, sys: 331 ms, total: 1min 29s
# Wall time: 1min 30s

%time trips = pd.read_csv('data/divvy/Divvy_Trips_2013.csv', converters={'starttime': to_datetime, 'stoptime': to_datetime})
# CPU times: user 17.6 s, sys: 269 ms, total: 17.9 s
# Wall time: 17.9 s

# $ wc -l divvy/Divvy_Trips_2013.csv 
#   759789 divvy/Divvy_Trips_2013.csv
