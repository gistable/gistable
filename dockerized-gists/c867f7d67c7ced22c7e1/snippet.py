#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2015 Erico Vieira Porto
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# This is a loose translation of the Yahoo Weather API Condition Codes from en-us
# to pt-br (Brazilian Portuguese). I needed this for a twitter bot.
# Source of the original Condition Codes is here:
# https://developer.yahoo.com/weather/documentation.html#codes
# If you have better translations, please send me: https://github.com/ericoporto/

ywcc_ptbr = {
    '0':  'tornado',                       # tornado
    '1':  'tempestade tropical',           # tropical storm
    '2':  'furacão',                       # hurricane
    '3':  'tempestade severa',             # severe thunderstorms
    '4':  'trovoadas',                     # thunderstorms
    '5':  'chuva e neve',                  # mixed rain and snow
    '6':  'chuva e granizo fino',          # mixed rain and sleet
    '7':  'neve e granizo fino',           # mixed snow and sleet
    '8':  'garoa gélida',                  # freezing drizzle
    '9':  'garoa',                         # drizzle
    '10': 'chuva gélida',                  # freezing rain
    '11': 'chuvisco',                      # showers
    '12': 'chuva',                         # showers
    '13': 'neve em flocos finos',          # snow flurries
    '14': 'leve precipitação de neve',     # light snow showers
    '15': 'ventos com neve',               # blowing snow
    '16': 'neve',                          # snow
    '17': 'chuva de granizo',              # hail
    '18': 'pouco granizo',                 # sleet
    '19': 'pó em suspensão',               # dust
    '20': 'neblina',                       # foggy
    '21': 'névoa seca',                    # haze
    '22': 'enfumaçado',                    # smoky
    '23': 'vendaval',                      # blustery
    '24': 'ventando',                      # windy
    '25': 'frio',                          # cold
    '26': 'nublado',                       # cloudy
    '27': 'muitas nuvens (noite)',         # mostly cloudy (night)
    '28': 'muitas nuvens (dia)',           # mostly cloudy (day)
    '29': 'parcialmente nublado (noite)',  # partly cloudy (night)
    '30': 'parcialmente nublado (dia)',    # partly cloudy (day)
    '31': 'céu limpo (noite)',             # clear (night)
    '32': 'ensolarado',                    # sunny
    '33': 'tempo bom (noite)',             # fair (night)
    '34': 'tempo bom (dia)',               # fair (day)
    '35': 'chuva e granizo',               # mixed rain and hail
    '36': 'quente',                        # hot
    '37': 'tempestades isoladas',          # isolated thunderstorms
    '38': 'tempestades esparsas',          # scattered thunderstorms
    '39': 'tempestades esparsas',          # scattered thunderstorms
    '40': 'chuvas esparsas',               # scattered showers
    '41': 'nevasca',                       # heavy snow
    '42': 'tempestades de neve esparsas',  # scattered snow showers
    '43': 'nevasca',                       # heavy snow
    '44': 'parcialmente nublado',          # partly cloudy
    '45': 'chuva com trovoadas',           # thundershowers
    '46': 'tempestade de neve',            # snow showers
    '47': 'relâmpagos e chuvas isoladas',  # isolated thundershowers
    '3200': 'não disponível'               # not available
}
