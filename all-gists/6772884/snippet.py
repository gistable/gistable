#!/usr/bin/env python
#
# file: scrapple.py
#
# description: checks apple.come for iphone 5s in-store pickup availability
#
# usage: ./scrapple.py [zip] [att|verizon|sprint] [16|32|64] [grey|silver|gold]
#
#  or in a crontab:
#  */5 * * * * /path/to/scrapple.py 10012 verizon 32 grey && mailx -s 5s 2125551212@vtext.com
#

import sys
from urllib import urlencode
from urllib2 import urlopen
import json
import smtplib

carrier_codes = {'att': 305,
                 'verizon': 341,
                 'sprint': 350}
storage_offset = {'16': 0,
                  '32': 3,
                  '64': 6}
color_offset = {'grey': 0,
                'silver': 1,
                'gold': 2}

BASE_URL = 'http://store.apple.com/us/retail/availabilitySearch'

def get_part_num(carrier, storage, color):
    num = carrier_codes[carrier] + storage_offset[storage] + color_offset[color]
    return 'ME%dLL/A' % num

if __name__=='__main__':
    zip, carrier, storage, color = sys.argv[1:]

    part_num = get_part_num(carrier, storage, color)

    query = urlencode({'parts.0': part_num, 'zip': zip})
    url = '%s?%s' % (BASE_URL, query)
    response = json.load(urlopen(url))

    stores = []
    for store in response['body']['stores']:
        availability = store["partsAvailability"][part_num]["pickupDisplay"]
        if availability != "unavailable":
            stores.append((store["storeDisplayName"], availability))

    if len(stores) > 0:
        msg = '%s %sGB %s\n' % (carrier, storage, color)
        msg += "\n".join([": ".join(store) for store in stores])

        print msg
        sys.exit(0)
    else:
        sys.exit(1)