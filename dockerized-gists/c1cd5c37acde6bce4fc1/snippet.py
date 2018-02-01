#!/usr/bin/env python

import shodan

API_KEY = 'YOUR API KEY'

api = shodan.Shodan(API_KEY)
results = api.count('port:443,8443', facets=[('ssl.cert.serial', 100)])

for facet in results['facets']['ssl.cert.serial']:
	print 'Serial %s occurs %s times' % (facet['value'], facet['count'])
