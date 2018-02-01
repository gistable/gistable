#!/usr/bin/python
import random
import string
import twitter

from fuzzywuzzy import process

api = twitter.Api()
recent_tweets = api.GetUserTimeline('andymboyle')
tweet_list = [tweet.text for tweet in recent_tweets]

random_string = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(140))

best_match = process.extractOne(random_string, tweet_list)

print best_match
