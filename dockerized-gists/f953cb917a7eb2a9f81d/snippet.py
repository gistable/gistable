#!/usr/bin/env python
#
# shodan-stream.py
# Read a firehose/ stream of 1% of the data that Shodan collects in real-time.
#
# WARNING: This script only works with people that have a subscription API plan!
# And by default the Streaming API only returns 1% of the data that Shodan gathers.
# If you wish to have more access please contact us at support@shodan.io for pricing
# information.
#
# Author: achillean

import shodan
import sys

# Configuration
API_KEY = 'YOUR API KEY'

try:
    # Setup the api
    api = shodan.Shodan(API_KEY)

    for banner in api.stream.banners():
    	print banner
except Exception, e:
    print 'Error: %s' % e
    sys.exit(1)
