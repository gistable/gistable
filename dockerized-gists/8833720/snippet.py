#!/usr/bin/env python
"""
A simple script to search Shodan and output the results as JSON-encoded banners;
each line corresponds to a single banner.

Warning: This will use up query credits because it pages through the results!

Usage: python simple-export.py <search query>
"""
# Install via "easy_install shodan"
import shodan

# Install via "easy_install simplejson", it's more resilient than the default json package
import simplejson

# For accessing the command-line arguments
import sys

api = shodan.Shodan('YOUR API KEY')

for banner in api.search_cursor(sys.argv[1:]):
    print simplejson.dumps(banner)