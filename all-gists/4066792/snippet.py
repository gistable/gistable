#!/usr/bin/env python2
"""Delete tweets older than X days.

Usage:

    rmtweets.py [at_least_days_old (default=365)]
"""

# Twitter gives access to only the last 3200 tweets, but if you delete
# more recent tweets, then after some time (a week? a month?) the
# script will be able to access and wipe older tweets too.

import twitter

from operator import itemgetter
from os.path import expanduser, exists
from sys import argv, exit, stderr
from time import time, mktime, strptime

APPNAME = "Twi Event Horizon"
DELETE_AFTER_X_DAYS = 365
# two lines per file: consumer key, consumer secret
CONSUMER_KEYS = expanduser("~/.twi-event-horizon.keys")
# two lines per file: auth token, auth token secret (obtained in oauth_dance)
AUTH_TOKENS = expanduser("~/.twi-event-horizon.tokens")

def read_keys(fname, n=2):
    f = open(fname)
    ks = []
    for i in xrange(n):
        k = f.readline().strip()
        ks.append(k)
    return ks

def ask_consumer_keys():
    if not exists(CONSUMER_KEYS):
        print "Register your application and obtain keys."
        ckey = raw_input("Consumer key: ").strip()
        csecret = raw_input("Consumer secret: ").strip()
        f = open(CONSUMER_KEYS, "w")
        print >>f, ckey
        print >>f, csecret
        return ckey, csecret
    else:
        return read_keys(CONSUMER_KEYS)

def ask_permissions(ckey, csecret):
    if not exists(AUTH_TOKENS):
        tokens = twitter.oauth_dance(APPNAME, ckey, csecret, AUTH_TOKENS)
        return tokens
    else:
        return read_keys(AUTH_TOKENS)

def authenticate():
    "Authenticate and return Twitter object."
    ckey, csecret = ask_consumer_keys()
    token, tsecret = ask_permissions(ckey, csecret)
    auth = twitter.OAuth(token,tsecret, ckey, csecret)
    t = twitter.Twitter(auth=auth)
    return t

def fetch_tweets(t):
    tweets = []
    min_id = None
    get_id = itemgetter("id")
    while True:
        if min_id:
            tl = t.statuses.user_timeline(count=200,
                                          include_rts=True,
                                          max_id=min_id)
        else:
            tl = t.statuses.user_timeline(count=200,
                                          include_rts=True)
        print "fetched %d tweets; rate limit remaining: %d" % \
              (len(tl), tl.rate_limit_remaining)
        if len(tl) <= 0:
            break
        tweets.extend(list(tl))
        new_min_id = min(map(get_id, tweets))
        if new_min_id == min_id:
            break  # twitter doesn't give anymore, limit of 3200 reached?
        else:
            min_id = new_min_id
        if tl.rate_limit_remaining < 0:
            break
    return tweets

def tweet_time(tweet):
    d = tweet["created_at"]
    t = strptime(d, "%a %b %d %H:%M:%S +0000 %Y")
    return mktime(t)

def main(horizon_days):
    t = authenticate()
    tweets = fetch_tweets(t)
    now = time()
    for tweet in tweets:
        days_old = (now - tweet_time(tweet))/86400
        if horizon_days < days_old:
            try:
                print "deleting",tweet["id"],"(%d days old)"%int(days_old)
                print ">", tweet["text"]
                t.statuses.destroy(id=tweet["id"])
            except twitter.api.TwitterHTTPError, e:
                print >>stderr, e

if __name__ == "__main__":
    if "--help" in argv[1:] or "-h" in argv[1:]:
        print __doc__
        exit(0)

    if argv[1:]:
        horizon = int(argv[1])
    else:
        horizon = DELETE_AFTER_X_DAYS
    main(horizon)
