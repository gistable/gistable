#!/usr/bin/python

'''
[INFORMATION]
script_name=WEATHER
description=consult weather using a weather id
language=english
programming_language=python3
author= Ander Raso Vázquez @ander_raso

[HOW IT WORKS]
$ weather.py # default location forecast
$ weather.py <weather id> # custom location forecast
$ weather.py 10001 # New York forecast

[DEPENDENCIES]
pywapi, colorama
'''

######################################################
############## CONFIGURATION #########################

location = 'SPXX0016' #  weather_id, default = Bilbao
debug_mode = False # for develovers

######################################################
######################################################

import pywapi # take weather information
from colorama import Back # color support
from sys import argv # pass system argument for custom location

class Weather:
    def __init__(self, weather_id, **kwargs):
        self._info = pywapi.get_weather_from_yahoo(weather_id, 'metric')
        self.variables = kwargs

    def set_variable(self, k, v):
        self.variables[k] = v

    def set_variables(self, **kwargs):
        self.variables.update(kwargs)

    def current_conditions(self):
        self.variables.update(
                temp = self._info['condition']['temp'],
                place = self._info['condition']['title']
                )
        s = "{place} - {temp}ºC".format(**self.variables)
        return s

    def astronomy(self):
        self.variables.update(
                sunrise = self._info['astronomy']['sunrise'],
                sunset  = self._info['astronomy']['sunset']
                )
        s = "Sunrise: {sunrise} Sunset: {sunset}".format(**self.variables)
        return s 

    def forecast(self, d):
        self.set_variables(
                            day = self._info['forecasts'][d]['day'],
                            date = self._info['forecasts'][d]['date'],
                            high = self._info['forecasts'][d]['high'],
                            low = self._info['forecasts'][d]['low'],
                            prev = self._info['forecasts'][d]['text']
                            )
        s = "{day} {date} Max: {high}ºC Min: {low}ºC Prev: {prev}".format(**self.variables)
        return s

    def get_variable(self, k):
        return self.variables.get(k, "That variable doesn't exist")

def main():
    def custom_report(o, weather_id, r1, r2):
        o = Weather(weather_id)
        print(Back.GREEN + o.current_conditions() + Back.RESET )
        print(o.astronomy())
        for d in range(r1,r2): print(o.forecast(d))

    if debug_mode == False:
        if len(argv) > 1:
            try:
                custom_report("custom_location", weather_id = argv[1], r1 = 0, r2 = 5)
            except:
                raise TypeError("Weather id not valid!")
        else:
            custom_report("default_location", weather_id = location, r1 = 0, r2 = 5)
    else:
        print("debug_mode = True")

if __name__ == "__main__": main()
