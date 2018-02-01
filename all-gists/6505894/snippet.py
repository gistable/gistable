# -*- coding:utf-8 -*-
'''
Simplistic script to parse the detailed AWS billing CSV file.

Script displays cost of S3 operations broken down per region, bucket and usage 
type (either storage or network). It also sums up the amount of storage used per bucket. 
Output is filtered wrt to costs < 1$.

See http://docs.aws.amazon.com/awsaccountbilling/latest/about/programaccess.html for 
how to set up programmatic access to your billing.

Should be simple enough to enhance this script and use it for other AWS resources 
(EC2, EMR, etc)

@author: @oddskool <https://github.com/oddskool>
@license: BSD 3 clauses
'''

import sys
import csv
from collections import defaultdict

def add_type(d):
    if d['RecordType'] == 'UsageQuantity':
        return None
    for field in ('Cost', 'UsageQuantity'):
        d[field] = float(d[field])
    for field in ('LinkedAccountId', 'InvoiceID', 'RecordType', 'RecordId',
                  'PayerAccountId', 'SubscriptionId'):
        del d[field]
    return d

def parse(stats, d):
    d = add_type(d)
    if not d:
        return
    if d['ProductName'] != 'Amazon Simple Storage Service':
        return
    stats[(d['AvailabilityZone'] or 'N/A')+' * '+d['ResourceId']+' * '+d['UsageType']]['Cost'] += d['Cost']
    stats[(d['AvailabilityZone'] or 'N/A')+' * '+d['ResourceId']+' * '+d['UsageType']]['UsageQuantity'] += d['UsageQuantity']

if __name__ == '__main__':
    fd = open(sys.argv[1]) if len(sys.argv) > 1 else sys.stdin
    reader = csv.reader(fd, delimiter=',', quotechar='"')
    legend = None
    stats = defaultdict(lambda: defaultdict(int))
    for row in reader:
        if not legend:
            legend = row    
            continue
        d = dict(zip(legend, row))
        try:
            parse(stats, d)
        except Exception as e:
            print e
            print row
            print d
    data = [ (resource, cost_usage) for resource, cost_usage in 
             stats.iteritems() if cost_usage['Cost'] > 1.0 ]
    data.sort(key=lambda x:x[-1]['Cost'], reverse=True)
    for d in data:
        print "%50s : $%.2f - %.2f GB" % (d[0],d[1]['Cost'],d[1]['UsageQuantity'])
