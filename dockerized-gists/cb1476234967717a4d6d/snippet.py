#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from datetime import timedelta
import json
import datetime
import re
import sys
import getopt

try:
    from urllib.request import Request, urlopen
except ImportError:  # python 2
    from urllib2 import Request, urlopen

__author__ = 'arulraj'

DEFAULT_STOCK_CODE_LIST = [
    "INDEXBOM:SENSEX",
    "NSE:NIFTY",
    "INDEXBOM:BSE-100",
    "INDEXBOM:BSE-200",
    "INDEXBOM:BSE-500",
    "INDEXBOM:BSE-SMLCAP",
    "INDEXBOM:BSE-MIDCAP",
    "NSE:NIFTYJR"
]

INTERVAL_REGEX = [r'[0-9]+d', r'[0-9]+m', r'[0-9]+y']

# DEFAULT_INTERVAL = ['5D', '1M', '3M', '6M', '1Y']
DEFAULT_INTERVAL = ['1M', '3M', '6M']

given_intervals = None

# TODO :
# if day greater than 50 convert that to month


class Interval(object):
    """

    """
    def __init__(self, _numeric_, _alphabet_):
        self.alphabet = _alphabet_.upper()
        self.numeric = int(_numeric_)

    @classmethod
    def build(cls, str_value):

        if Interval.is_valid_interval(str_value):
            match_obj = re.search(r"[0-9]+", str_value, re.I)
            numeric = match_obj.group(0)
            match_obj = re.search(r"[dmy]", str_value, re.I)
            alphabet = match_obj.group(0)
            return cls(numeric, alphabet)
        else:
            print "The interval '%s' is not valid" % str_value

    @staticmethod
    def is_valid_interval(str_interval):
        for i_pattern in INTERVAL_REGEX:
            match_obj = re.match(i_pattern, str_interval, re.IGNORECASE)
            if match_obj:
                return True

    def as_table_header(self):
        return "v_" + str(self)

    def __str__(self):
        return ''.join([str(self.numeric), self.alphabet])

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        """
        This is will not take difference between 120D and 4M.
        """
        if self.alphabet < other.alphabet:
            return -1
        elif self.alphabet > other.alphabet:
            return 1
        else:
            if self.numeric < other.numeric:
                return -1
            elif self.numeric > other.numeric:
                return 1
            else:
                return 0


class Quote(object):
    """
    Referred from http://trading.cheno.net/downloading-google-intraday-historical-data-with-python/
    """
    def __init__(self):
        self.symbol = ''
        self.exchange = ''
        self.date, self.time, self.open_, self.high, self.low, self.close, self.volume = ([] for _ in range(7))

    def append(self, dt, open_, high, low, close, volume):
        self.date.append(dt.date())
        self.time.append(dt.time())
        self.open_.append(float(open_))
        self.high.append(float(high))
        self.low.append(float(low))
        self.close.append(float(close))
        self.volume.append(int(volume))

    def to_csv(self):
        return ''.join(["{0},{1},{2},{3:.2f},{4:.2f},{5:.2f},{6:.2f},{7}\n".format(self.symbol,
                                                                                   self.date[bar].strftime('%Y-%m-%d'),
                                                                                   self.time[bar].strftime('%H:%M:%S'),
                                                                                   self.open_[bar], self.high[bar],
                                                                                   self.low[bar], self.close[bar],
                                                                                   self.volume[bar])
                        for bar in xrange(len(self.close))])

    def __str__(self):
        return self.to_csv()

    def __repr__(self):
        return self.to_csv()


def get_current_stock_info():
    """

    :return:
    """
    symbol_list = ','.join([stock for stock in given_stock_codes])
    stocks_url = 'http://finance.google.com/finance/info?client=ig&q=' \
                 + symbol_list
    content = get_content(stocks_url)
    content = content[3:]
    return content


def get_history_stock_info(exchange, stock_name, interval_seconds, _range):
    """

    :param exchange:
    :param stock_name:
    :param interval_seconds:
    :param _range:
    :return:
    """
    stock_name = stock_name.upper()
    url_string = "http://www.google.com/finance/getprices?"
    url_string += "q={0}&x={1}".format(stock_name, exchange)
    url_string += "&i={0}&p={1}&f=d,o,h,l,c,v".format(interval_seconds, _range)
    csv = get_content(url_string, is_list=True)
    quotes = []
    for bar in xrange(7, len(csv)):
        if csv[bar].count(',') != 5:
            continue
        offset, close, high, low, open_, volume = csv[bar].split(',')
        if offset[0] == 'a':
            day = float(offset[1:])
            offset = 0
        else:
            offset = float(offset)
        open_, high, low, close = [float(x) for x in [open_, high, low, close]]
        dt = datetime.datetime.fromtimestamp(day + (interval_seconds * offset))

        q = Quote()
        q.append(dt, open_, high, low, close, volume)
        quotes.append(q)
    return quotes


def stock_low_high_info(intervals):
    """

    :param intervals:
    :return:
    """
    stock_low_high_dict = dict()

    from datetime import datetime

    now = datetime.now()

    for stock_code in given_stock_codes:
        exchange_name = stock_code.split(":")[0]
        stock_name = stock_code.split(":")[1]
        intervals_sort = sorted(intervals)
        _range = str(intervals_sort[-1])
        if intervals_sort[-1].alphabet == "D":
            _range = _range.lower()
        quotes = get_history_stock_info(exchange_name, stock_name, 86400, _range)

        high_low_dict = dict()

        for interval in intervals_sort:

            interval_time = None
            if interval.alphabet == "D":
                interval_time = daydelta(now, -interval.numeric)
            elif interval.alphabet == "M":
                interval_time = monthdelta(now, -interval.numeric)
            elif interval.alphabet == "Y":
                interval_time = yeardelta(now, -interval.numeric)

            quotes_in_interval = [q for q in quotes if q.date[0] > interval_time.date()]
            sort_by_close = sorted(quotes_in_interval, key=lambda x: x.close)

            if len(sort_by_close) > 0:
                high_low_dict[str(interval)] = {"low": sort_by_close[0].close[0],
                                                "high": sort_by_close[len(sort_by_close) - 1].close[0]}

        if len(high_low_dict.keys()) > 0:
            stock_low_high_dict[stock_name] = high_low_dict

    return stock_low_high_dict


def get_content(url, is_list=False):
    """
    Get content of url as string
    :return:
    """
    req = Request(url)
    resp = urlopen(req)
    if is_list:
        content = resp.readlines()
    else:
        content = resp.read().decode('ascii', 'ignore').strip()
    return content


def parse_content(content):
    """
    Combine current stock info and history stock information into StockInfo object.

    :param content:
    :return:
    """
    stock_resp_list = json.loads(content)

    interval_list = list()
    table_header_list = list()

    for i in given_intervals:
        interval = Interval.build(i)
        if interval:
            interval_list.append(interval)
            table_header_list.append(interval.as_table_header())

    stock_high_low_dict = dict()
    if len(interval_list) > 0:
        stock_high_low_dict = stock_low_high_info(interval_list)

    default_header = ["Index", "Current", "Change_pts", "Updated_on"]
    default_header.extend(table_header_list)

    StockInfo = namedtuple("StockInfo", default_header)

    list_stock = list()
    for stock_resp in stock_resp_list:

        stock_high_low = dict()
        if stock_resp["t"] in stock_high_low_dict:
            stock_high_low = stock_high_low_dict[stock_resp["t"]]

        i_high_low_list = list()
        for interval in interval_list:
            i_high_low_value = ""
            if str(interval) in stock_high_low:
                i_high_low = stock_high_low[str(interval)]
                i_high_low_value = "⇓ %s, ⇑ %s" % (i_high_low["low"], i_high_low["high"])
            i_high_low_list.append(i_high_low_value)

        stockInfo = StockInfo(stock_resp["t"], stock_resp["l"], "%s(%s%%)" % (stock_resp["c"], stock_resp["cp"]),
                              stock_resp["lt"], *i_high_low_list)
        list_stock.append(stockInfo)
    return list_stock


def pprinttable(rows):
    """
    Referred From http://stackoverflow.com/a/5910078/458701 and modified bit to support UTF-8

    :param rows:
    :return:
    """
    if len(rows) > 1:
        headers = rows[0]._fields
        lens = []
        for i in range(len(rows[0])):
            lens.append(len(max([x[i] for x in rows] + [headers[i]], key=lambda x: len(str(x)))))
        formats = []
        hformats = []
        for i in range(len(rows[0])):
            if isinstance(rows[0][i], int):
                formats.append("%%%dd" % lens[i])
            else:
                formats.append("%%-%ds" % lens[i])
            hformats.append("%%-%ds" % lens[i])
        pattern = " | ".join(formats)
        hpattern = " | ".join(hformats)
        separator = "-+-".join(['-' * n for n in lens])
        print hpattern % tuple(headers)
        print separator
        _u = lambda t: t.decode('UTF-8', 'replace') if isinstance(t, str) else t
        for line in rows:
            print pattern % tuple(_u(t) for t in line)
    elif len(rows) == 1:
        row = rows[0]
        hwidth = len(max(row._fields, key=lambda x: len(x)))
        for i in range(len(row)):
            print "%*s = %s" % (hwidth, row._fields[i], row[i])


def monthdelta(date, delta):
    """

    :param date: datetime object
    :param delta: negative value will subtract from given date. positive value will add from given date.
    :return:
    """
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m: m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def daydelta(date, delta):
    """

    :param date: datetime object
    :param delta: negative value will subtract from given date. positive value will add from given date.
    :return:
    """
    return date + timedelta(hours=24 * delta)


def yeardelta(date, delta):
    """

    :param date: datetime object
    :param delta: negative value will subtract from given date. positive value will add from given date.
    :return:
    """
    return date + timedelta(weeks=52 * delta)


if __name__ == "__main__":
    """
    How to use
    - Copy this into /usr/local/bin folder as 'stockmarketindia'
    - chmod +x /usr/local/bin/stockmarketindia
    - Run `stockmarketindia` as command from anywhere in your terminal
    - Detailed info
        - stockmarketindia -i 5d,1m,3m,6m,1y
    """

    given_intervals = list()
    given_stock_codes = DEFAULT_STOCK_CODE_LIST
    # given_intervals = DEFAULT_INTERVAL

    try:
        myopts, args = getopt.getopt(sys.argv[1:], "s:i:")
    except getopt.GetoptError as e:
        print (str(e))
        print("Usage: %s -i intervals. For ex: %s -i 5D,1M,1Y" % (sys.argv[0], sys.argv[0]))
        sys.exit(2)

    for o, a in myopts:
        if o == '-i':
            a_list = str(a).split(',')
            given_intervals = a_list
        if o == '-s':
            a_list = str(a).split(',')
            given_stock_codes = a_list

    json_content = get_current_stock_info()
    stock_info_list = parse_content(json_content)
    pprinttable(stock_info_list)