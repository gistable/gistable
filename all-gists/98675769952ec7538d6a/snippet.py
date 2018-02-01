#!/usr/bin/env python
#coding:utf-8

# Exchange usd to any currency, or any currency to usd
# help: python convert_usd.py -h

import os.path
from datetime import date, datetime
import argparse
import urllib
import json

URL = "http://api.aoikujira.com/kawase/json/usd"
FPATH = "/tmp/exchange"


def hasCache():
    if os.path.isfile(FPATH):
        d = date.today()
        today = datetime.combine(d, datetime.min.time())
        mtime = datetime.fromtimestamp(os.path.getmtime(FPATH))
        if mtime > today:
            return True
    return False


def readCache():
    with open(FPATH, 'r') as f:
        body = f.read()
    return body


def writeCache(body):
    with open(FPATH, 'w') as f:
        f.write(body)


def fetchRates():
    # fetch rate list from remote
    response = urllib.urlopen(URL)
    body = response.read()

    writeCache(body)

    return body


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='convert usd to any currency.')
    parser.add_argument('-p', '--price', nargs='?', type=float, help='price', default=1.0)
    parser.add_argument('-c', '--currency', nargs='?', help='currency', default=u'JPY')
    parser.add_argument('-r', '--reverse', action='store_true', help='reverse the direction')
    parser.add_argument('-v', '--verbosity', action='count', help='increase output verbosity')

    args = parser.parse_args()
    price = args.price
    currency = args.currency
    reverse = args.reverse
    verbosity = args.verbosity

    if hasCache():
        body = readCache()
    else:
        body = fetchRates()

    data = json.loads(body)
    rate = float(data[currency])

    if reverse:
        if verbosity >= 1:
            print "{0}({2}) => {1}(USD)".format(1, 1 / rate, currency)
            print "{0}({2}) => {1}(USD)".format(price, price / rate, currency)
        else:
            print price / rate
    else:
        if verbosity >= 1:
            print "{0}(USD) => {1}({2})".format(1, rate, currency)
            print "{0}(USD) => {1}({2})".format(price, price * rate, currency)
        else:
            print price * rate
