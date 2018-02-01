#!/usr/bin/env python
#
# Generates non-unique word list from Twitter Search meeting certain
# criteria (as set in the configuration, below).
#
# EXAMPLE (word wrap inserted for ease of reading):
#
# $ python hashtag_wordle.py 
# Fetching http://search.twitter.com/search.json?q=%23spinuzzi-project&rpp=30&page=1...
# Fetching http://search.twitter.com/search.json?q=%23spinuzzi-project&rpp=30&page=2...
# 
# about added allusion alternative ambient atelier austin austin's
# became better business capital capital casual chocolate class clay'
# comments conjectures could couple courtesy creative
# creativity=invention credit crowds crowdwhoring crunkarbeit
# deliworking diaspora didnt digital directions dispersion entries
# entries flickr florida's freelance funtastic funtastic going great
# handle hashtag hashtag invest investment jelly looking looking loose
# loose melancing music networks office organizational other places
# pretty project project really reminder reshape rhetorical riding
# search should smart social spaces still still stories structures
# suggest suggestions thanks through title title titles titles
# tomorrow tweet twitter under untold using weird welcome while winner
# workability workatoriums workatoriums worker working workplace
# workspaces would would wouldn't y'all
# 

import re
import sys
import urllib
import urllib2
from pprint import pprint

import jsonlib as json

##############################################################################
# CONFIGURATION
##############################################################################

ALLOWED_REGEX = "^[a-zA-Z'=]+$"
HASH_TAG = '#spinuzzi-project'
MIN_LENGTH = 4

##############################################################################
# BEGIN ZE CODES
##############################################################################

def main():
    updates = []
    url = "http://search.twitter.com/search.json"
    params = {"q": HASH_TAG,
              "rpp": 30,
              "page": 1}

    while True:
        req_data = urllib.urlencode(params)
        print >>sys.stderr, "Fetching %s?%s..." % (url, req_data)

        req = urllib2.Request(url, req_data)
        response = urllib2.urlopen(req)
        contents = response.read()
        info = json.loads(contents)

        updates += [update for update in info['results']]
        if not len(info['results']):
            break
        else:
            params['page'] += 1
            req_data = urllib.urlencode(params)

    all_words = []
    banned = [HASH_TAG]
    allowed_re = re.compile(ALLOWED_REGEX)
    
    for result in updates:
        words = result['text'].split(" ")
        all_words += [word.lower()
                      for word in words
                      if (word not in banned and
                          allowed_re.match(word) and
                          len(word) > MIN_LENGTH)]

    print("")
    print(" ".join(sorted(all_words)))

if __name__ == '__main__':
    main()
