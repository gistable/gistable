#!/usr/bin/python

import sys
import os
from Foundation import NSDate

from Foundation import NSPredicate

def doComparison(comp_string, obj):
    print 'Comparison: %s' % comp_string
    try:
        p = NSPredicate.predicateWithFormat_(comp_string)
    except Exception, e:
        print >> sys.stderr, "WARNING: %s" % e
        print False
        print
        return
        
    print p.evaluateWithObject_(obj)
    print

info = {}
info['os_vers'] = '10.8.2'
info['os_vers_patch'] = 2
info['arch'] = 'x86_64'
info['munki_version'] = '0.8.3.1489.0'
info['catalogs'] = ['testing', 'production']
info['ip_addresses'] = ['172.30.161.160', '172.30.157.57']
info['ip_address'] = '172.30.161.160'
info['date'] = NSDate.date()
info['machine_model'] = 'MacBookAir5,2'

print info
print

predicate = 'NOT machine_model BEGINSWITH "MacBookAir"'
doComparison(predicate, info)

comparisonstring = 'nonexistent == nil'
doComparison(comparisonstring, info)

comparisonstring = 'machine_model LIKE "*Book*"'
doComparison(comparisonstring, info)

comparisonstring = 'date > CAST("2013-01-02T00:00:00Z", "NSDate")'
doComparison(comparisonstring, info)

comparisonstring = 'CAST(date, "NSString") > "2013-01-02T00:00:00Z"'
doComparison(comparisonstring, info)

comparisonstring = 'date > CAST("2012-12-19T11:00:00Z", "NSDate")'
doComparison(comparisonstring, info)

comparisonstring = 'NOT catalogs CONTAINS "development"'
doComparison(comparisonstring, info)

comparisonstring = 'smurf LIKE "10.7*"'
doComparison(comparisonstring, info)

comparisonstring = 'os_vers IN {"10.7.1", "10.7.2", "10.7.11"}'
doComparison(comparisonstring, info)

comparisonstring = 'os_vers MATCHES "10\.7.*"'
doComparison(comparisonstring, info)

comparisonstring = 'os_vers BEGINSWITH "10.7"'
doComparison(comparisonstring, info)

comparisonstring = 'os_vers BEGINSWITH "10.6"'
doComparison(comparisonstring, info)

comparisonstring = 'os_vers >= "10.7.1"'
doComparison(comparisonstring, info)

comparisonstring = 'os_vers >= "10.7.3"'
doComparison(comparisonstring, info)

comparisonstring = 'munki_version >= "0.8.3.1489.0"'
doComparison(comparisonstring, info)

comparisonstring = 'arch = "x86_64"'
doComparison(comparisonstring, info)

comparisonstring = 'arch = "i386"'
doComparison(comparisonstring, info)

comparisonstring = 'arch = "x86_64" OR arch = "i386"'
doComparison(comparisonstring, info)

comparisonstring = 'arch CONTAINS "86"'
doComparison(comparisonstring, info)

comparsionstring = 'arch = "x86_64" AND os_vers > "10.7.2"'
doComparison(comparsionstring, info)

comparsionstring = 'ip_addresses CONTAINS "172.30.161"'
doComparison(comparsionstring, info)

comparsionstring = 'ip_addresses[0] LIKE "172.30.161.*"'
doComparison(comparsionstring, info)

comparsionstring = 'ANY ip_addresses LIKE "172.30.161."'
doComparison(comparsionstring, info)

comparsionstring = '(os_vers BEGINSWITH "10.7" AND os_vers_patch >= 5) OR (os_vers BEGINSWITH "10.8" AND os_vers_patch >= 2)'
doComparison(comparsionstring, info)