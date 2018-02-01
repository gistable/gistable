# script to download up to <= 3200 (the official API limit) of most recent tweets from a user's timeline 
from pymongo import MongoClient

import tweepy
import json

#Twitter API credentials
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''


class TwitterHarvester(object):
    """Create a new TwitterHarvester instance"""
    def __init__(self, consumer_key, consumer_secret,
                 access_token, access_token_secret,
                 wait_on_rate_limit=False,
                 wait_on_rate_limit_notify=False):

        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.secure = True
        self.auth.set_access_token(access_token, access_token_secret)
        self.__api = tweepy.API(self.auth,
                                wait_on_rate_limit=wait_on_rate_limit,
                                wait_on_rate_limit_notify=wait_on_rate_limit_notify)
    
    @property
    def api(self):
        return self.__api

def twitter_logic():
    # instantiate an object of TwitterHarvester to use it's api object
    # make sure to set the corresponding flags as True to whether or 
    # not automatically wait for rate limits to replenish
    a = TwitterHarvester(CONSUMER_KEY, CONSUMER_SECRET, 
                         ACCESS_TOKEN, ACCESS_TOKEN_SECRET,
                         wait_on_rate_limit=True,
                         wait_on_rate_limit_notify=True)
    api = a.api

    # assume there's MongoDB running on the machine, get a connection to it
    conn = MongoClient('localhost', 27017)
    db = conn['twitter_db']
    collection = db['tweets']

    # use the cursor to skip the handling of the pagination mechanism 
    # http://docs.tweepy.org/en/latest/cursor_tutorial.html
    tweets = tweepy.Cursor(api.user_timeline, screen_name="cnnbrk").items()
    while True:
        # as long as I still have a tweet to grab
        try:
            data = tweets.next()
        except StopIteration:
            break
        # convert from Python dict-like structure to JSON format
        jsoned_data = json.dumps(data._json)
        tweet = json.loads(jsoned_data)
        # insert the information in the database
        collection.insert(tweet)


if __name__ == "__main__":
    twitter_logic()