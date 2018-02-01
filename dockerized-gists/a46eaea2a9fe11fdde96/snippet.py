# coding: utf-8

# Copyright 2015 Álvaro Justen <https://github.com/turicas/rows/>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# requirements:
#   pip install requests

# Other useful URLs:
#  http://www.bmfbovespa.com.br/cotacoes2000/FormConsultaCotacoes.asp?strListaCodigos=BBPO11|PETR4
#  http://www.bmfbovespa.com.br/Pregao-Online/ExecutaAcaoAjax.asp?CodigoPapel=BBPO11|PETR4
#  http://www.bmfbovespa.com.br/cotacoes2000/formCotacoesMobile.asp?codsocemi=BBPO11

import datetime

from collections import namedtuple
from decimal import Decimal

import requests


URL = 'http://www.bmfbovespa.com.br/Pregao-Online/executaacaocarregardadosPapeis.asp?CodDado={symbol}'
MONTHS = {'Jan': '01', 'Fev': '02', 'Mar': '03', 'Abr': '04', 'Mai': '05',
          'Jun': '06', 'Jul': '07', 'Ago': '08', 'Set': '09', 'Out': '10',
          'Nov': '11', 'Dez': '12',}
StockQuote = namedtuple('StockQuote', ['timestamp', 'price', 'oscilation'])

def create_date(date, time):
    year, month, day = date.split('/')
    month = MONTHS[month]
    hour, minute, second = time.split(':')
    return datetime.datetime(int(year), int(month), int(day), int(hour),
                             int(minute), int(second))

def create_stock_quote(date, value):
    return StockQuote(create_date(date, value[0]),
                      Decimal(value[1]),
                      Decimal(value[2]))

def parse_intraday_data(data):
    """Parse BMF API data into a list of `StockQuote` objects"""

    data_dict = dict([x.split('=') for x in data.split('&')])
    date = data_dict['D']
    values = [value.split('@') for value in data_dict['V'].split('|') if value]
    return [create_stock_quote(date, value) for value in values]

def get_quote(symbol):
    """Get data from BMF Bovespa API (used by its Android app)"""
    response = requests.get(URL.format(symbol=symbol))
    return parse_intraday_data(response.content)

def test_parse_intraday_data():
    data = 'D=2015/Mai/28&V=10:00:00@103.15@-0.02|16:47:04@103@-0.17|&CE=0&ME='
    expected_response = [
        StockQuote(timestamp=datetime.datetime(2015, 5, 28, 10, 0, 0),
                   price=Decimal('103.15'),
                   oscilation=Decimal('-0.02')),
        StockQuote(timestamp=datetime.datetime(2015, 5, 28, 16, 47, 04),
                   price=Decimal('103.0'),
                   oscilation=Decimal('-0.17')), ]
    assert parse_intraday_data(data) == expected_response


if __name__ == '__main__':
    print 'Quotes for BBPO11 today:'
    for quote in get_quote('BBPO11'):
        print '  {} {}'.format(quote.timestamp, quote.price)