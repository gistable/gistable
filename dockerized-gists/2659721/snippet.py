#!/usr/bin/python

from pyquery import PyQuery as pq
import re
import datetime

print datetime.datetime.now().strftime('%c')
print

doc = pq(url='http://www.beermenus.com/places/4733-the-ruck')

beers = []

for tr in [pq(tr) for tr in doc('table.beermenu tbody tr')]:
    if tr('td').length < 4:
        continue
    name = tr('td:first-child a').text()
    serving_info = re.match(r'(\d+)\s*oz\.?\s+(\w+)', tr('.serving').text())
    ounces = int(serving_info.group(1))
    serving = serving_info.group(2)
    # We append a zero because some ABV values are empty on the page
    abv = float(tr('.abv').text() + '0')
    price = float(tr('.price').text().replace('$', '').split()[0])
    # Efficiency metric: "ounces of pure alcohol in $100 worth of beer".
    # In other words, booze for your buck.
    efficiency = (ounces * abv) / price
    beers.append({
        'name': name,
        'ounces': ounces,
        'serving': serving,
        'abv': abv,
        'price': price,
        'efficiency': efficiency
    })

for beer in sorted(beers, key=lambda b: b['efficiency']):
    line = "%-45s\n\t%2d-oz %-6s %4.1f%% ABV, $%-5.2f (Eff'cy: %5.2f)" % (
        beer['name'][:45], beer['ounces'], beer['serving'],
        beer['abv'], beer['price'], beer['efficiency'])
    print line.encode('utf-8')
