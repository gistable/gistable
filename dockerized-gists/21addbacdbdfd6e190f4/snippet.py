#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
import json

try:
    from urllib.request import Request, urlopen
except ImportError:  # python 2
    from urllib2 import Request, urlopen

__author__ = 'arulraj'

STOCK_CODE_LIST = [
    "INDEXBOM:SENSEX",
    "NSE:NIFTY",
    "INDEXBOM:BSE-100",
    "INDEXBOM:BSE-200",
    "INDEXBOM:BSE-500",
    "INDEXBOM:BSE-SMLCAP",
    "INDEXBOM:BSE-MIDCAP",
    "NSE:NIFTYJR"
]

Stock = namedtuple("Stock", ["Index", "Current", "Change_pts", "Change_percent", "Updated_on"])

def build_url():
    """

    :return:
    """
    symbol_list = ','.join([stock for stock in STOCK_CODE_LIST])
    return 'http://finance.google.com/finance/info?client=ig&q=' \
        + symbol_list


def get_content(url):
    """

    :return:
    """
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode('ascii', 'ignore').strip()
    content = content[3:]
    return content


def parse_content(content):
    """

    :param content:
    :return:
    """
    stock_resp_list = json.loads(content)

    list_stock = list()
    for stock_resp in stock_resp_list:
      isPositive = False if stock_resp["cp"] != None and len(stock_resp["cp"]) > 0 and stock_resp["cp"][0] == '-' else True

      colored_cp = stock_resp["cp"]
      if isPositive:
          colored_cp = Color.green(stock_resp["cp"])
      else:
          colored_cp = Color.red(stock_resp["cp"])

      list_stock.append(Stock(stock_resp["t"], stock_resp["l"], stock_resp["c"], colored_cp, stock_resp["lt"]))

    return list_stock


def pprinttable(rows):
    """
    From http://stackoverflow.com/a/5910078/458701 and modified bit to support UTF-8

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


def preety_print_stock(stock_list, preety=True):
    """

    :param stock_list:
    :return:
    """
    if not preety:
        print """"%s", "%s", "%s", "%s", "%s" """ % (Stock._fields)
        for stock in stock_list:
            print """"%s", "%s", "%s", "%s", "%s" """ % (stock[0], stock[1], stock[2], stock[3], stock[4])
    else:
        pprinttable(stock_list)


class Color(object):
    """
    reference from https://gist.github.com/Jossef/0ee20314577925b4027f and modified bit.

    """

    def __init__(self, text, **user_styles):

        styles = {
            # styles
            'reset': '\033[0m',
            'bold': '\033[01m',
            'disabled': '\033[02m',
            'underline': '\033[04m',
            'reverse': '\033[07m',
            'strike_through': '\033[09m',
            'invisible': '\033[08m',
            # text colors
            'fg_black': '\033[30m',
            'fg_red': '\033[31m',
            'fg_green': '\033[32m',
            'fg_orange': '\033[33m',
            'fg_blue': '\033[34m',
            'fg_purple': '\033[35m',
            'fg_cyan': '\033[36m',
            'fg_light_grey': '\033[37m',
            'fg_dark_grey': '\033[90m',
            'fg_light_red': '\033[91m',
            'fg_light_green': '\033[92m',
            'fg_yellow': '\033[93m',
            'fg_light_blue': '\033[94m',
            'fg_pink': '\033[95m',
            'fg_light_cyan': '\033[96m',
            # background colors
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_orange': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_purple': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_light_grey': '\033[47m'
        }

        self.color_text = ''
        for style in user_styles:
            try:
                self.color_text += styles[style]
            except KeyError:
                raise KeyError('def color: parameter `{}` does not exist'.format(style))

        self.color_text += text

    def __format__(self):
        return '{}\033[0m\033[0m'.format(self.color_text)

    @classmethod
    def red(clazz, text):
        cls = clazz(text, bold=True, fg_red=True)
        return cls.__format__()

    @classmethod
    def orange(clazz, text):
        cls = clazz(text, bold=True, fg_orange=True)
        return cls.__format__()

    @classmethod
    def green(clazz, text):
        cls = clazz(text, bold=True, fg_green=True)
        return cls.__format__()

    @classmethod
    def custom(clazz, text, **custom_styles):
        cls = clazz(text, **custom_styles)
        return cls.__format__()


if __name__ == "__main__":
    json_content = get_content(build_url())
    stock_list = parse_content(json_content)
    preety_print_stock(stock_list, True)
