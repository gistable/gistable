#!/usr/bin/env python
"""
Parse a HAR (HTTP Archive) and return URLs which resulted in a given HTTP response code
HAR Spec: http://groups.google.com/group/http-archive-specification/web/har-1-2-spec
Copyleft 2010 Ian Gallagher <crash@neg9.org>

Example usage: ./har_response_urls.py foo.har 404
"""

import json

if '__main__' == __name__:
    import sys

    if len(sys.argv) < 3:
        print "Usage: %s <har_file> <HTTP response code>" % sys.argv[0]
        sys.exit(1)

    har_file = sys.argv[1]
    response_code = int(sys.argv[2])

    # Read HAR archive (skip over binary header if present - Fiddler2 exports contain this)
    har_data = open(har_file, 'rb').read()
    skip = 3 if '\xef\xbb\xbf' == har_data[:3] else 0

    har = json.loads(har_data[skip:])

    matching_entries = filter(lambda x: response_code == x['response']['status'], har['log']['entries'])
    matching_urls = set(map(lambda x: x['request']['url'], matching_entries))
    
    print >>sys.stderr, "URLs which resulted in an HTTP %d response:" % response_code
    for url in matching_urls:
        print url