#!/usr/bin/env python


# Example for reading from the Twitter streaming API using pycurl
#
# PyCurl is not installed by default so install it like this:
#
#     pip install pycurl
#
# The streaming api methods are documented here:
#
#     http://dev.twitter.com/pages/streaming_api_methods#statuses-links
#
# In short, you have 'filter', 'firehose', 'links', 'retweet' and 'sample'
# Some of those methods require special access, as documented
#
# James Dennis - jdennis@gmail.com


import pycurl
import urllib
import json


FIREHOSE_URL = "http://stream.twitter.com/1/statuses/%s.json"


def attach_nozzle(api_fun, callback, args, username, password):
    nozzle_url = FIREHOSE_URL % api_fun

    conn = pycurl.Curl()
    conn.setopt(pycurl.USERPWD, "%s:%s" % (username, password))
    conn.setopt(pycurl.URL, nozzle_url)
    conn.setopt(pycurl.WRITEFUNCTION, callback)

    data = urllib.urlencode(args)
    conn.setopt(pycurl.POSTFIELDS, data)

    conn.perform()


def hose(data):
    print data
    # write stuff to database or something...


if __name__ == "__main__":
    username = "********"
    password = "********"

    # This varies for each nozzle
    args = {
    }

    attach_nozzle('sample', hose, args, username, password)
