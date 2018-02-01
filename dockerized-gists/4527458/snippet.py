#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<1@binux.me>
#         http://binux.me
# Created on 2013-01-14 10:29:51

import re
import cPickle
import requests

rss = 'http://decodeingress.me/feed/'
cookie = ''
csrf = re.findall('csrftoken=(\w+)', cookie)[0]

try:
    checked = cPickle.load(open('checked.passcode'))
except:
    checked = []

for title in re.findall(r'<title>(.*?)</title>', requests.get(rss).text):
    if 'passcode' not in title.lower():
        continue
    for each in title.split(' '):
        each = each.strip()
        if 'passcode' in each.lower():
            continue
        if each in checked:
            continue
        r = requests.post('http://www.ingress.com/rpc/dashboard.redeemReward',
                data = '{"passcode": "%s", "method":"dashboard.redeemReward"}' % each,
                headers = {
                    'Cookie': cookie,
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrf,
                    })
        checked.append(each)
        print each, r.text

try:
    cPickle.dump(checked, open('checked.passcode', 'w'))
except:
    pass