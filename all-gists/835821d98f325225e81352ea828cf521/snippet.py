"""
Parse fullOrders.csv downloaded from Bittrex account.

Requirements::

  pip install dateparser

"""

import csv
import sys
from subprocess import check_call, CalledProcessError

from dateparser import parse


field_mapping = {
    'Opened': {'name': 'TimeStamp', 'ftype': parse},
    'Closed': {'name': 'Closed', 'ftype': parse},
    'Price': {'name': 'Price', 'ftype': float},
    'Quantity': {'name': 'Quantity', 'ftype': float},
    'Exchange': {'name': 'Exchange', 'ftype': str},
    'Type': {'name': 'Type', 'ftype': str},
    'CommissionPaid': {'name': 'Comission', 'ftype': float},
    'Limit': {'name': 'Limit', 'ftype': float},
    'OrderUuid': {'name': 'OrderUuid', 'ftype': str}
}

PATH_TO_FILE = sys.argv[1]

# workaround for _csv.Error: line contains NULL byte
try:
    check_call("sed -i -e 's|\\x0||g' {}".format(PATH_TO_FILE), shell=True)
except CalledProcessError as err:
    print(err)

# parse csv
with open(PATH_TO_FILE, 'r') as f:
    reader = csv.DictReader(f)
    orders = []
    for row in reader:
        order = {}
        for key in row.keys():
            fmap = field_mapping.get(key)
            real_key = fmap.get('name')
            order[real_key] = fmap.get('ftype')(row.get(key))
        orders.append(order)

print('Found {0} orders.'.format(len(orders)))
