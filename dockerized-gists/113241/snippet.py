# -*- coding: utf-8 -*-
"""
This script will delete all of the tweets in the specified account.
You may need to hit the "more" button on the bottom of your twitter profile
page every now and then as the script runs, this is due to a bug in twitter.

You will need to get a consumer key and consumer secret token to use this
script, you can do so by registering a twitter application at https://dev.twitter.com/apps

@requirements: Python 2.5+, Tweepy (http://pypi.python.org/pypi/tweepy/1.7.1)
@author: Dave Jeffery
"""

import tweepy

CONSUMER_KEY = 'XXX'
CONSUMER_SECRET = 'XXX'

def oauth_login(consumer_key, consumer_secret):
    """Authenticate with twitter using OAuth"""
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_url = auth.get_authorization_url()
    
    verify_code = raw_input("Authenticate at %s and then enter you verification code here > " % auth_url) 
    auth.get_access_token(verify_code)
    
    return tweepy.API(auth)

def batch_delete(api):
    print "You are about to Delete all tweets from the account @%s." % api.verify_credentials().screen_name
    print "Does this sound ok? There is no undo! Type yes to carry out this action."
    do_delete = raw_input("> ")
    if do_delete.lower() == 'yes':
        for status in tweepy.Cursor(api.user_timeline).items():
            try:
                api.destroy_status(status.id)
                print "Deleted:", status.id
            except:
                print "Failed to delete:", status.id

if __name__ == "__main__":
    api = oauth_login(CONSUMER_KEY, CONSUMER_SECRET)
    print "Authenticated as: %s" % api.me().screen_name
    
    batch_delete(api)