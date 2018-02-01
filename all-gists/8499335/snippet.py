import re
from cPickle import dump
from requests import get

DEFAULT_TICKERS = ['goog', 'aapl']
URL = 'http://www.sec.gov/cgi-bin/browse-edgar?CIK={}&Find=Search&owner=exclude&action=getcompany'
CIK_RE = re.compile(r'.*CIK=(\d{10}).*')

cik_dict = {}
for ticker in DEFAULT_TICKERS:
    results = CIK_RE.findall(get(URL.format(ticker)).content)
    if len(results):
        cik_dict[str(ticker).lower()] = str(results[0])
f = open('cik_dict', 'w')
dump(cik_dict, f)
f.close()