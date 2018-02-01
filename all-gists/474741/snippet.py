#!/usr/bin/python

"""
Simple script to pull user's tweets and place those with location information into a SimpleGeo layer.
Based on the Twitter wrapper Tweepy and SimpleGeo's Foursquare example.
(http://blog.simplegeo.com/post/790366330/foursquare-simplegeo)

If a tweet has associated location coordinates, these are added to the record.
Twitter places, described by bounding boxes, are not added to the record.

Make sure to enter your own SimpleGeo OAUTH key and secret as well as your Twitter username.
Also enter the name of the layer you wish to append in SimpleGeo.

This assumes your Twitter account is not protected.
"""

import simplegeo
import time
import feedparser
import tweepy

import datetime
from simplegeo import Client, Record, APIError

MY_OAUTH_KEY = 'YOUR_OAUTH_KEY'
MY_OAUTH_SECRET = 'YOUR_OAUTH_SECRET'
MY_LAYER = 'YOUR_LAYER_NAME'
MY_TWITTER_USERNAME = 'YOUR_TWITTER_USERNAME'
records = []

def main():
    tweet_ids = []
    client = Client(MY_OAUTH_KEY, MY_OAUTH_SECRET)
    my_tweets = tweepy.api.user_timeline(MY_TWITTER_USERNAME)
    print "\n\n" 
        
    for tweet in my_tweets:
        if (tweet.geo):
            lat = tweet.geo['coordinates'][0]
            lng = tweet.geo['coordinates'][1]
        else:
            lat = 0
            lng = 0
        
        if (tweet.place):
            place_name = tweet.place['full_name']
            place_URL = tweet.place['url']
        else: 
            place_name = "None"
            place_URL = "None"
                             
        tweet_URL = "http://twitter.com/" + tweet.user.screen_name + "/" + str(tweet.id)
        created_t = tweet.created_at - datetime.timedelta(seconds=7*60*60)
        created_t = int(time.mktime(created_t.timetuple()))
        if (tweet.geo):
            record = Record(
		        layer=MY_LAYER,
		        id=str(tweet.id),
		        lat=lat,
		        lon=lng,
		        created=created_t,
		        text=tweet.text,
		        URL=tweet_URL,
		        type="object"
	        )
            print "\nCreated record with ID: %s" % record.id
            records.append(record)
  
    for chunk in chunker(records, 90):
        client.add_records(MY_LAYER, chunk)
        print "\n%s records added" % len(chunk)

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


if __name__ == '__main__':
    main()
