#!/usr/bin/env python3
from urllib.request import urlopen
from xml.dom.minidom import parseString
import os
"""
Request current weather from Yahoo's public weather API and append to a log
"""
# Where to put the log file?
desired_path = os.getenv("HOME") + '/weather.log'
# Temperature unit: c for Celsius, f for Fahrenheit
desired_unit = 'f'
# From which location?
# Use http://woeid.rosselliot.co.nz/lookup/ to get the correct code
# No automatic lookup due to lack of API key. Sorry.
desired_location = 2459115 # this is New York


url = ('http://weather.yahooapis.com/forecastrss?u=' + desired_unit +
    '&w=' + str(desired_location))
reply = urlopen(url)
encoding = reply.headers['Content-type'].split('charset=')[1]
xml = reply.read().decode(encoding)
doc = parseString(xml)

atmosphere_Elems = doc.getElementsByTagName('yweather:atmosphere')[0]
condition_Elems = doc.getElementsByTagName('yweather:condition')[0]
wind_Elems = doc.getElementsByTagName('yweather:wind')[0]

pressure = atmosphere_Elems.getAttribute('pressure')
humidity = atmosphere_Elems.getAttribute('humidity')
temp = condition_Elems.getAttribute('temp')
condition_text = condition_Elems.getAttribute('text')
report_date = condition_Elems.getAttribute('date')
windspeed = wind_Elems.getAttribute('speed')
wind_direction = wind_Elems.getAttribute('direction')

first_line_is_needed = not os.path.isfile(desired_path)
with open(desired_path, 'a') as logfile:
    # If the file didn't exist before, prepend column titles
    if first_line_is_needed:
        print('Date', 'Temp', 'Condition', 'Pressure', 'Humidity', 'Windspeed',
            'Wind Direction', sep='\t', end='\n', file=logfile)
    print(report_date, temp, condition_text, pressure, humidity, windspeed,
        wind_direction, sep='\t', end='\n', file=logfile)