#!/usr/bin/env python3
"""Show current wheather in Moscow, Russia in terminal and web browser.

   http://weather.yandex.ru
   http://stackoverflow.com/q/20308901
"""
import xml.etree.ElementTree as etree
from urllib.request import urlopen

# https://github.com/emacsmirror/yandex-weather/blob/master/yandex-weather.el
city_id = 27612 # Moscow, Russia
weather_url = "https://export.yandex.ru/weather-ng/forecasts/%d.xml" % city_id

ns = lambda tag: "{http://weather.yandex.ru/forecast}" + tag # add namespace

class Data(dict):
    def __missing__(self, key):
        return root.find(ns('fact')).findtext(ns(key))

# download & parse xml with weather forecast
root = etree.parse(urlopen(weather_url)).getroot()

# print current weather
data = Data(city=root.get('city'))
text = (u"""{observation_time}: {city}
    {temperature} °C, {weather_type}""".format_map(data))
print(text)

# show it in browser
import html
import tempfile
import time
import webbrowser

icon_url_format = ("https://yandex.st/weather/1.2.1/i/icons/22x22/"
                   "{image-v2}.png")

def open_in_browser(html):
    """like lxml.html.open_in_browser() but `html` is a bytestring."""
    with tempfile.NamedTemporaryFile("wb", suffix='.html', buffering=0) as file:
        file.write(html)
        webbrowser.open(file.name)
        time.sleep(60) # give the browser a minute to open before
                       # deleting the file

open_in_browser(u'''<!doctype html>
    <meta charset="utf-8">
    <link href="{icon_url}" rel="icon" />
    <title>{text}</title>
    <img src="{icon_url}" alt="{weather_type}">
    <p>{text}
'''.format(text=html.escape(text),
           icon_url=html.escape(icon_url_format.format_map(data)),
           weather_type=html.escape(data['weather_type'])).encode('utf-8'))
