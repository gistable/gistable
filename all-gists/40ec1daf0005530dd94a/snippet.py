#!/usr/bin/env python

from datetime import datetime
from json import loads
from time import gmtime, mktime, strptime

# LevelDict é um wrapper usando dicionário para LevelDB
# https://github.com/maurobaraldi/leveldict
from leveldict import LevelJsonDict
from requests import get

base = 'http://cotacoes.economia.uol.com.br/ws/asset'
assets = base + '/stock/list?size=10000'
intraday = base + '/{asset}/intraday?size=400&callback=uolfinancecallback0'
assets = {i['code']: i['idt'] for i in get(assets).json()['data']}

# 3 ativos para teste
# assets = {'PETR4.SA': 484, 'CTAX4.SA': 227, 'IGUA3.SA': 364}

db = LevelJsonDict('./intraday')


def from_ts(ts):
    ''' Convert timestamp (13 digits support) to datetime'''
    return datetime.fromtimestamp(mktime(gmtime(ts / 1000.0)))


def to_ts(dt):
    ''' From strftime to timestamp (13 digits support)'''
    return int(mktime(strptime(dt, "%Y-%m-%d %H:%M")) * 1000)


def get_intraday(asset):
    url = intraday.format(**{'asset': asset})
    return loads(get(url).content[20:-2])


if __name__ == '__main__':
    for asset, code in assets.iteritems():
        today = datetime.now().strftime('%Y%m%d')
        quote = get_intraday(code).get('data', {})
        db.setdefault(asset)
        db[asset] = {today: quote}
