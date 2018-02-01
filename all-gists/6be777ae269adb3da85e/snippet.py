#! /usr/bin/env python

import urllib.request
import json
import subprocess
import time
import sys

url ="https://www.ovh.com/js/dedicatedAvailability/availability-data"
ks1_key = "142sk1"  # KS-1, the cheapest box they have

def available():
    data = urllib.request.urlopen(url).read()
    data = json.loads(data.decode('utf-8'))
    availability = [d['zones'] for d in data['availability'] if d['reference'] == ks1_key][0]
    availability = [d['availability'] for d in availability if d['availability'] != 'unavailable']
    return availability != []


if __name__ == '__main__':
    while True:
        try:
            av = available()
        except:
            time.sleep(2)
            continue
        if av:
            print('Y', end='')
            subprocess.call(['notify-send', 'OVH servers available'])
        else:
            print('.', end='')
        sys.stdout.flush()
        time.sleep(2)
