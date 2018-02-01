from TwitterSearch import *
import json

try:
    tso = TwitterSearchOrder()
    tso.set_keywords(['#BOSC2015'])
    # Please replace with your credentials
    ts = TwitterSearch(
        consumer_key='REPLACE_ME',
        consumer_secret='REPLACE_ME',
        access_token='REPLACE_ME',
        access_token_secret='REPLACE_ME'
    )
    for tweet in ts.search_tweets_iterable(tso):
        print(json.dumps(tweet))
except TwitterSearchException as e:
    print(e)