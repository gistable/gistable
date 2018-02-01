"""
Created by Christian Stade-Schuldt on 2014-07-28.
"""

import sqlite3
import json
import urllib
import time
import datetime
import calendar

APP_ID = YOUR_APP_ID
WEATHER_DATA_URL = 'http://api.openweathermap.org/data/2.5/weather?q=Berlin,de&units=metric&APPID=' + APP_ID


def get_data():
    """get weather data from openweathermap"""
    response = urllib.urlopen(WEATHER_DATA_URL)
    data = json.loads(response.read())

    temp = data['main']['temp']
    pressure = data['main']['pressure']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    try:
        wind_gust = data['wind']['gust']
    except KeyError:
        wind_gust = None
    wind_deg = data['wind']['deg']
    clouds = data['clouds']['all']
    try:
        rain = data['rain']['3h']
    except KeyError:
        rain = None
    try:
        snow = data['snow']['3h']
    except KeyError:
        snow = None
    weather_id = data['weather'][0]['id']
    sunrise = data['sys']['sunrise']
    sunset = data['sys']['sunset']

    return [temp, pressure, temp_min, temp_max, humidity, wind_speed, wind_gust, wind_deg, clouds, rain, snow,
            weather_id, sunrise, sunset]


def save_data_to_db(data):
    con = sqlite3.connect("PATH_TO_SQLITE_FILE")
    con.isolation_level = None
    cur = con.cursor()

    query = '''INSERT INTO weather_data VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

    cur.execute(query, tuple([datetime.datetime.now().isoformat()] + data[:-2]))

    con.commit()
    con.close()


def main():
    data = get_data()
    time.sleep(10)
    now = calendar.timegm(datetime.datetime.now().timetuple())
    if data[-2] < now < data[-1]:
        save_data_to_db(data)


if __name__ == '__main__':
    main()
