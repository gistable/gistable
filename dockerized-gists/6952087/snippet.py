#!/usr/bin/env python
"""
Get financial data from Google Finance.

Requirment:
  pyquery 1.2.6.   (1.2.1 did not work)

Report types:
inc - income statement
bal - balance sheet
cas - cash flow


usage: google_finance.py [-h] [-m MARKET] [-r {inc,bal,cas}]
                         [-t {annual,interim}] [-c CSV]
                         [symbol]

positional arguments:
  symbol                symbol

optional arguments:
  -h, --help            show this help message and exit
  -m MARKET, --market MARKET
                        market string
  -r {inc,bal,cas}, --report-type {inc,bal,cas}
                        report type
  -t {annual,interim}, --term {annual,interim}
                        report term
  -c CSV, --csv CSV     CSV file name
"""
import csv
import re
import sys
from datetime import date
from decimal import Decimal
from pyquery import PyQuery as pq

GOOGLE_FINANCE_REPORT_TYPES = {
    'inc': 'Income Statement',
    'bal': 'Balance Sheet',
    'cas': 'Cash Flow',
}
DATE = re.compile(".*(\d{4})-(\d{2})-(\d{2}).*")


class GoogleFinance(object):
    """
    Get financial data from Google Finance.

    aapl = GoogleFinance('NASDAQ', 'AAPL')
    print aapl.cash_flow()

    """
    GOOGLE_FINANCE_URL = "https://www.google.com/finance?q={}:{}&fstype=ii"

    def __init__(self, market, symbol):
        self.market = market.upper()
        self.symbol = symbol.upper()
        self._financial = None

    @staticmethod
    def _parse_number(s):
        """
        return decimal object if the given string is parseable as number.
        return None if the string is -
        otherwise return the string as is
        """
        if s == '-':
            return None
        try:
            return Decimal(s.replace(',', ''))
        except Exception, _:
            pass
        return s

    @staticmethod
    def _parse_date(s):
        """
        return datetime object if the given string contains YYYY-MM-DD string
        otherwise return the string as is
        """
        m = DATE.match(s)
        if m:
            return date(*[int(e) for e in m.groups()])
        return s

    @staticmethod
    def to_csv(csv_file_name, report):
        with open(csv_file_name, 'w') as fp:
            writer = csv.writer(fp, delimiter=',', quotechar='"',
                                quoting=csv.QUOTE_NONNUMERIC)
            for row in report:
                writer.writerow(row)

    def _get_from_google(self):
        return pq(self.GOOGLE_FINANCE_URL.format(self.market, self.symbol))

    def _get_table(self, report_type, term):
        assert term in ('interim', 'annual')
        assert report_type in ('inc', 'bal', 'cas')

        if not self._financial:
            self._financial = self._get_from_google()

        div_id = report_type + term + 'div'
        return self._financial('div#{} table#fs-table'.format(div_id))

    def _statement(self, stmt_type, term):
        tbl = self._get_table(stmt_type, term)
        ret = []
        for row in tbl.items('tr'):
            data = [self._parse_number(i.text()) for i in row.items('th, td')]
            if not ret:
                data = [self._parse_date(e) for e in data]
            ret.append(data)
        return zip(*ret)

    def income_statement(self, term='annual'):
        return self._statement('inc', term)

    def balance_sheet(self, term='annual'):
        return self._statement('bal', term)

    def cash_flow(self, term='annual'):
        return self._statement('cas', term)


def main(args):
    google_finance = GoogleFinance(args.market, args.symbol)
    financial_report = None
    if args.report_type == 'inc':
        financial_report = google_finance.income_statement(args.report_term)
    elif args.report_type == 'bal':
        financial_report = google_finance.balance_sheet(args.report_term)
    elif args.report_type == 'cas':
        financial_report = google_finance.cash_flow(args.report_term)

    if not financial_report:
        print "{} {} financial report not available for {}:{}".format(
            args.report_term.title(), GOOGLE_FINANCE_REPORT_TYPES.get(args.report_type, 'Unknown'),
            google_finance.market, google_finance.symbol)
        sys.exit()

    if args.csv:
        google_finance.to_csv(args.csv, financial_report)
    else:
        print financial_report


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='get financial data from Google Finance')
    parser.add_argument('-m', '--market', type=str,
                        action='store', dest='market',
                        help='market string', default='NASDAQ')
    parser.add_argument('-r', '--report-type', type=str,
                        help='report type', default='inc',
                        action='store', dest='report_type',
                        choices=['inc', 'bal', 'cas'])
    parser.add_argument('-t', '--term', type=str,
                        help='report term', default='annual',
                        action='store', dest='report_term',
                        choices=['annual', 'interim'])
    parser.add_argument('-c', '--csv', type=str,
                        help='CSV file name', action='store')
    parser.add_argument('symbol', action='store', type=str, nargs='?',
                        help='symbol')
    args = parser.parse_args()

    if not args.symbol:
        print "please supply symbol"
        sys.exit()

    main(args)
