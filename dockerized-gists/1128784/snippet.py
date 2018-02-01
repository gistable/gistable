#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from pyquery import PyQuery as pq

doc = pq(url='http://www.jinakrajina.cz/cz/poledni-menu')
noms = doc.find('td > p')
print '\n%s'%noms[0].text_content()[2:]
for i,nom in enumerate(noms[1:-1:2],1):
    print '[%d] %s'%(i,nom.text_content().strip())

print '\n=====\n'

doc = pq(url='http://www.lemonleaf.cz/lunch_buffet_menu.php')
noms = doc.find('div > dl')[datetime.date.today().weekday()].iterchildren()
for i in noms:
    print i.text_content().strip(),noms.next().text_content().strip()