# -*- coding: utf-8 -*-

import sys
import requests
import lxml.html


def main(i):
    url = 'http://www.posti.fi/itemtracking/posti/search_by_shipment_id?lang=en&ShipmentId'
    result = {'details': [], 'events': []}

    p = requests.get('{0}={1}'.format(url, i))
    page = lxml.html.fromstring(p.text)
    details = page.xpath('//table[@id="shipment-details-table"]/tr')

    if not details:
        raise Exception('Tracking ID %s not found' % i)

    for i in details:
        result['details'].append((i[0].text_content(), i[1].text_content(),))

    events = page.xpath('//table[@id="shipment-event-table"]/tbody/tr/td/div')

    for i in events:
        result['events'].append(i.text_content().strip("\n"))

    return result


if __name__ == '__main__':
    for x in sys.argv[1:]:
        d = main(x)
        for i in d['details']:
            print('{0: <32} {1}'.format(i[0].encode('utf-8'), i[1].encode('utf-8')))
        for i in d['events']:
            print(i)
