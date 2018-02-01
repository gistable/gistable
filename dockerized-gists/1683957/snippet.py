#!/usr/bin python
"""
requires simplejson module (https://github.com/simplejson/simplejson)

Usage example:

tail -f /var/log/json.log | grep "muratcorlu.com" | python json.py log.date log.url
"2011.12.14 14:21" "http://muratcorlu.com/post/archieve/"
"2011.12.14 14:29" "http://muratcorlu.com/"

"""
import sys
import simplejson as json

for line in sys.stdin:
        data = json.loads(line)
        args = sys.argv[1:]
        if (len(args) > 0):
                for param in args:
                        nested = param.split('.')
                        value = data.get( nested[0] )
                        nested = nested[1:]

                        for key in nested:
                                value = value.get(key)

                        print json.dumps( value ),
                print ""
