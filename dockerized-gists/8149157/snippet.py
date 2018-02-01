#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from HTMLParser import HTMLParser
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from prettytable import PrettyTable
import requests


CCAA_URL = 'http://www.correoargentino.com.ar/sites/all/modules/custom/ca_forms/api/ajax.php'
DATE_INPUT_NAT = '%d-%m-%Y %H:%M'
DATE_INPUT_INT = '%Y-%m-%d %H:%M'
DATE_OUTPUT = '%d-%b-%Y %H:%M'

parser = argparse.ArgumentParser(description='Verificar seguimientos de Correo Argentino.')
parser.add_argument('track_id_list', metavar='N', type=str, nargs='+',
                   help='IDs de los seguimientos')

args = parser.parse_args()
for track_id in  args.track_id_list:
    if track_id[-2:] == 'AR':
        data = {
            'action': 'ondnc',
            'id': track_id[2:-2],
            'pais': 'AR',
            'producto': track_id[:2],
        }
        DATE_INPUT = DATE_INPUT_NAT

    else:
        data = {
            'action': 'oidn',
            'id': track_id
        }
        DATE_INPUT = DATE_INPUT_INT

    print 'Buscando información para: %s ...' % track_id

    res = requests.post(CCAA_URL, data)
    html = BeautifulSoup(res.text)

    h = HTMLParser()
    table_list = html.findAll("table")

    table_1 = PrettyTable([th.getText() for th in table_list[0].find('thead').find('tr').findAll("th")])
    for row in table_list[0].find('tbody').findAll('tr'):
        data_row = [h.unescape(r.getText()) for r in row.findAll('td')]
        data_row[0] = datetime.strptime(data_row[0], DATE_INPUT).strftime(DATE_OUTPUT)
        table_1.add_row(data_row)

    print table_1

    if len(table_list) == 2:
        print ''
        for p in html.findAll('p'):
            try:
                p.getText().index("seguimiento nacional")
                local_track_id = p.find('span').getText().replace('-', '').replace('.', '')
                break
            except ValueError:
                pass

        print 'Track ID nacional: %s' % local_track_id
        table_2 = PrettyTable([th.getText() for th in table_list[-1].find('thead').find('tr').findAll("th")])
        for row in table_list[-1].findAll('tbody'):
            data_row = [h.unescape(r.getText()) for r in row.findAll('td')]
            data_row[0] = datetime.strptime(data_row[0], DATE_INPUT_NAT).strftime(DATE_OUTPUT)
            table_2.add_row(data_row)

        print table_2