# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 13:23:34 2016

@author: Brian Christopher, CFA [Blackarbs LLC]
"""

import pandas as pd
from  more_itertools import unique_everseen
import requests
from bs4 import BeautifulSoup as bs
import re

class barchart_options():
    # --------------------------------------------
    def __init__(self, symbol):
        self.symbol = symbol

        self.payload = {'email':'YOUR_EMAIL', 'password':'YOUR_PASSWORD'}
        self.base_url = r"http://www.barchart.com/options/stocks/"
        self.login_url = r'http://www.barchart.com/login.php'
        self.basic_URL = self.base_url + symbol
        self.base_SRC = self.__get_base_src()
        self.greeks_url_suffix = '&view=vol&sym={SYMBOL}&date={DATE}'
        self.reidx_cols = ['Symbol', 'Expiry', 'Type', 'Strike', 'Ask', 'Bid', 'Last', 'Change',
                           'Underlying_Price', 'ImpliedVolatility','TheoreticalValue', 'Delta',
                           'Gamma', 'Rho', 'Theta', 'Vega', 'Open Int', 'Volume']
    # --------------------------------------------
    # get basic options data source
    # --------------------------------------------
    def __get_base_src(self):
        with requests.session() as S:
            res = S.get(self.basic_URL)
        return bs(res.text, 'lxml')

    # --------------------------------------------
    # extract expiry dates
    # --------------------------------------------
    def _extract_expiry_dates(self):
        raw_date_links = []
        for link in self.base_SRC.find_all('a', href=re.compile('date')):
            raw_date_links.append(list(link.attrs.values())[0])

        reg_exp = r'[A-z]{3}-\d{2}-\d{4}'

        dates = []
        for raw_date in raw_date_links:
            ms = re.search(reg_exp, raw_date)
            dates.append(ms.group())
        return list(unique_everseen(dates))
    # --------------------------------------------
    # get option greeks source data
    # --------------------------------------------
    def __login_greeks(self, symbol, date):
        with requests.session() as S:
            _ = S.post(self.login_url, data=self.payload)
            res = S.get(self.__create_greeks_url(symbol, date))
        return bs(res.text, 'lxml')

    def __create_greeks_url(self, symbol, date):
        url = self.base_url + self.greeks_url_suffix.format(SYMBOL=symbol, DATE=date)
        return url

    def _get_greeks_src(self, symbol, date):
        src = self.__login_greeks(symbol, date)
        return src

    def __clean_headers(self, headers):
        hdr = headers.replace('\t', '').split('\n')
        hdrs = [hdr for hdr in hdr if len(hdr) > 0]
        return hdrs

    def __get_greek_headers(self, greek_src):
        hdrs = [head.get_text() for head in greek_src.find_all('tr', class_='datatable_header')][0]
        return self.__clean_headers(hdrs)

    def __get_greeks_tables(self, greek_src):
        tables = []
        for tbl in greek_src.find_all('table', class_='datatable'):
            tables.append(tbl)
        return tables
    # --------------------------------------------
    # create basic options dfs
    # --------------------------------------------
    def __get_underlying_last_price(self, greek_src):
        last = [float(d.text) for d in greek_src.find_all('span', class_='last')]
        return last

    def __create_base_call_df(self, expiry):
        tables = []
        for tbl in self.base_SRC.find_all('table', class_='datatable'):
            tables.append(tbl)
        call_rows = [[td.text for td in tr.find_all('td')] for tr in tables[0].find_all('tr')]
        cols = ['Strike', 'Symbol', 'Type', 'Bid', 'Ask', 'Last', 'Change', 'Volume', 'Open Int']
        call_df = pd.DataFrame(call_rows[1:], columns=cols).apply(pd.to_numeric, errors='ignore')
        return call_df

    def __create_base_put_df(self, expiry):
        tables = []
        for tbl in self.base_SRC.find_all('table', class_='datatable'):
            tables.append(tbl)
        put_rows = [[td.text for td in tr.find_all('td')] for tr in tables[1].find_all('tr')]
        cols = ['Strike', 'Symbol', 'Type', 'Bid', 'Ask', 'Last', 'Change', 'Volume', 'Open Int']
        put_df = pd.DataFrame(put_rows[1:], columns=cols).apply(pd.to_numeric, errors='ignore')
        return put_df
    # --------------------------------------------
    # create, merge basic and greek options dfs
    # --------------------------------------------
    def _create_calls_df(self, greek_src, expiry):
        tables = self.__get_greeks_tables(greek_src)
        rows = [[td.text for td in tr.find_all('td')] for tr in tables[0].find_all('tr')]
        calls = pd.DataFrame(rows[1:], columns=self.__get_greek_headers(greek_src)
                            ).apply(pd.to_numeric, errors='ignore')
        calls['Underlying_Price'] = self.__get_underlying_last_price(greek_src) * len(calls.index)
        calls['Expiry'] = [pd.to_datetime(expiry)] * len(calls.index)

        base_call_df = self.__create_base_call_df(expiry)
        mrg = calls.combine_first(base_call_df)
        CALLS = mrg.reindex(columns=self.reidx_cols)
        return CALLS

    def _create_puts_df(self, greek_src, expiry):
        tables = self.__get_greeks_tables(greek_src)
        rows = [[td.text for td in tr.find_all('td')] for tr in tables[1].find_all('tr')]
        puts = pd.DataFrame(rows[1:], columns=self.__get_greek_headers(greek_src)
                           ).apply(pd.to_numeric, errors='ignore')
        puts['Underlying_Price'] = self.__get_underlying_last_price(greek_src) * len(puts.index)
        puts['Expiry'] = [pd.to_datetime(expiry)] * len(puts.index)

        base_put_df = self.__create_base_put_df(expiry)
        mrg = puts.combine_first(base_put_df)
        PUTS = mrg.reindex(columns=self.reidx_cols)
        return PUTS
    # --------------------------------------------
