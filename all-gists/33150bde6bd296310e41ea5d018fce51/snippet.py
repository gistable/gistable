#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
1. Open Terminal
2. sudo easy_install pip
3. pip install --user requests
4. pip install --user requests_threads
5. pip install --user beautifulsoup4
6. pip install --user --upgrade pyopenssl
7. pip install --user service_identity
'''

from __future__ import print_function
import re
import sys

from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError, ReadTimeout
from requests_threads import AsyncSession
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import react

RESULTS_PER_PAGE=200
URL = 'http://www.nihon-kankou.or.jp/event?pref__=&city__=&purpose__=&keyword__=&rng__=&lat__=&lng__=&re_search__=true&linePerPage__={results_per_page}&event_list__=true&el_month1__=1%E6%9C%88&el_month2__=12%E6%9C%88&pageStart__={page_start}'

def scrape_page(r, f):
    if r.status_code is not 200:
        print('non 200 status code for url: %s' % r.url)
        sys.exit(1)
    soup = BeautifulSoup(r.text, 'html.parser')
    phone_info = soup.find(string=re.compile('TEL'))
    if phone_info is not None:
        phone_info = phone_info.encode('utf-8').strip().split(' ')
        if len(phone_info) == 2:
            phone_info = phone_info[1]
        elif len(phone_info): # handles both len == 1 and len > 2
            phone_info = ' '.join(phone_info)
    else:
        phone_info = 'No phone number'
    print(r.url, file=f)
    print(soup.find(id='detail_heading').h1.text.encode('utf-8').strip(), file=f)
    print(phone_info, file=f)
    print(soup.find('th', string=re.compile('所在地'.decode('utf-8'))).parent.td.text.encode('utf-8').strip().split('\n')[0], file=f)
    print('', file=f)

@inlineCallbacks
def main(reactor):
    with open('event_info.txt', 'w+') as f:
        session = AsyncSession(n=RESULTS_PER_PAGE)
        i = 0
        while True:
            print('%d events written...' % i)
            responses = []
            try:
                r = requests.get(URL.format(results_per_page=RESULTS_PER_PAGE, page_start=i), timeout=30)
            except ReadTimeout as e:
                print('timed out paging through URLs')
                sys.exit(1)
            if r.status_code is not 200:
                print('non 200 status code %d: i=%d' % (r.status_code, i))
                sys.exit(1)
            soup = BeautifulSoup(r.text, 'html.parser')
            try:
                results = soup.find(id='result_body').find(class_='list04').find_all('li')
            except AttributeError:
                print('invalid page')
                sys.exit(1)
            if not results:
                break
            for li in results:
                url = 'http://www.nihon-kankou.or.jp/%s' % li.find('a', href=True)['href']
                responses.append(session.get(url, timeout=30))
            for idx, r in enumerate(responses):
                try:
                    r = yield r
                except ConnectionError as e:
                    print('failed on request number: %d; please lower RESULTS_PER_PAGE' % idx)
                    raise e
                except ReadTimeout as e:
                    print('timed out requesting event page')
                    sys.exit(1)
                try:
                    scrape_page(r, f)
                except Exception:
                    print('error with url: %s' % r.url)
                    raise
            i += RESULTS_PER_PAGE

if __name__ == '__main__':
    react(main)