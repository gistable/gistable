#!/usr/bin/python
# -*- coding: utf-8 -*-

import tweepy
from random import choice

#Twitter Information
CONSUMER_KEY = "asdasdadasdads"
CONSUMER_SECRET="asdasdasdasd"
ACCESS_KEY="asdasdasdasd"
ACCESS_SECRET="asdasdasdasdasdsa"

#Authorization
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
API = tweepy.API(auth)


replys = ['WHO CARES?!',
	  'O RLY? http://i.imgur.com/VK1ey.jpg',
          'BOOORIIING http://i.imgur.com/XbdZo.jpg',
	  u'Nobody cares ¬¬',
	  'OK, here I go! http://i.imgur.com/gYGQp.gif',
	  'Thanks. Hold your hands up, I cant see you... http://i.imgur.com/juzKF.jpg'
	  'OK ... http://i.imgur.com/HneJA.jpg', 
	  'SO WHAT?!', 
	  'http://i.imgur.com/knK3O.jpg', 
	  'http://i.imgur.com/792lk.jpg']


API = tweepy.API(auth)

public = API.public_timeline()
for tweet in public:
    if tweet.source =='foursquare':
	API.update_status( "@"+ tweet.author.screen_name +" "+ choice(replys) , tweet.id)
	