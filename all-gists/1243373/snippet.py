#! /usr/bin/env python

# how to unfollow everyone who isn't following you
# By Jamieson Becker (Public Domain/no copyright, do what you will)

# Easy instructions, even if you don't know Python
#
# 1.  Install pip (apt-get install python-pip) and then
#     pip install tweepy, which is the python twitter client
#
# 2.  create a new app in your account at dev.twitter.com
#     and then plug in your consumer and app keys below.
#     Trim all whitespace at beginning/end of your keys.
#
# 3.  the twitter app needs to have permissions changed to
#     read-write, as apps are read-only by default.
# 
# 4.  Execute this script: python unfollow.py

import time
import tweepy
import sys

auth = tweepy.auth.OAuthHandler(
        consumer_key='foo',
        consumer_secret='bar')
auth.set_access_token(
        'foobaz',
        'foobar')

api=tweepy.API(auth_handler=auth)

print "Loading followers.."
follower_objects = [follower for follower in tweepy.Cursor(api.followers).items()]

print "Found %s followers, finding friends.." % len(followers)
friend_objects = [friend for friend in tweepy.Cursor(api.friends).items()]

# create dictionaries based on id's for easy lookup
friends = dict([(friend.id, friend) for friend in friend_objects])
followers = dict([(follower.id, follower) for follower in follower_objects])

# find all your "non_friends" - people who don't follow you even though you follow them.
non_friends = [friend for friend in friend_objects if friend.id not in followers]

# double check, since this could be a rather traumatic operation.
print "Unfollowing %s non-following users.." % len(non_friends)
print "This will take approximately %s minutes." % (len(non_friends)/60.0)
answer = raw_input("Are you sure? [Y/n]").lower()
if answer and answer[0] != "y":
    sys.exit(1)

# start the removal process. In the event of a failure (thanks, twitter!),
# retry once after five seconds. An error on same record again is
# probably more serious issue, so abort with error

for nf in non_friends:
    print "Unfollowing " + str(nf.id).rjust(10)
    try:
        nf.unfollow()
    except:
        print "  .. failed, sleeping for 5 seconds and then trying again."
        time.sleep(5)
        nf.unfollow()
    print " .. completed, sleeping for 1 second."
    time.sleep(1)
