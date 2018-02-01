#!/usr/bin/env python

def convert_mph(match):
    try:
        mph = int(match.group(0).split(' ')[0])
        kph = mph*1.6
        #return "%.1f kph" % (kph,)
        return "%s kph" % (int(round(kph)),)
    except:
        return match.group(0)


def get_weather_for_city(city):
    city = city.replace(' ', '+')

    url = 'http://www.google.com/ig/api?weather=' + city

    import urllib2

    # ElementTree in python before 2.7 is completely useless.
    # (and python doesn't come with any other "just parse the damn xml"
    #  libraries that just work.)
    # so I force ascii as I'm trying to make this work in 2.6
    # easy test case: Try this for Paris and see it break.
    #source = urllib2.urlopen(url).read().decode('utf8')

    source = urllib2.urlopen(url).read()
    source = source.decode('ascii', 'ignore')
    source = source.encode('ascii')

    from xml.etree import ElementTree as ET

    # before 2.7 ElementTree.fromstring() doesn't support an encoding parameter
    # or a unicode string.
    # I kid you not.
    etree = ET.fromstring(source)

    # before 2.7 ElementTree.XMLParser doesn't support the encoding parameter.
    # again: not a joke.
    #fp = urllib2.urlopen(url)
    #etree = ET.parse(fp, parser=ET.XMLParser(encoding='utf8'))

    weather = etree.find('weather')

    parts = []

    information = weather.find('forecast_information')
    city = information.find('city').get('data')
    parts.append("City: "+city)

    conditions = weather.find('current_conditions')

    temperature = conditions.find('temp_c').get('data') + 'C'
    parts.append('Temperature: '+temperature)

    humidity = conditions.find('humidity').get('data')
    parts.append(humidity)

    wind = conditions.find('wind_condition').get('data')
    import re
    wind = re.sub('\d+ mph', convert_mph, wind)
    parts.append(wind)

    condition = conditions.find('condition').get('data')
    parts.append('Condition: '+condition)

    return ', '.join(parts)

if __name__ == '__main__':
    # usage: ./weather.py cape town
    import sys
    city = ' '.join(sys.argv[1:])
    print get_weather_for_city(city).encode('utf8')
