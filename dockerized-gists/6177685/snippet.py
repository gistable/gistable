#!/usr/bin/python2
# -*- coding: utf-8 -*-

# autoblock.py
# Automagically blocks new followers if their account is not older than x 
# days, has not reached a minimum number of tweets and has not more than x
# followers.
#
# Dependencies: - Tweepy
#               - simplejson

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# nilsding <nilsding@nilsding.org> wrote this file. As long as you retain this
# notice you can do whatever you want with this stuff. If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------

# === CONFIG BEGINS HERE ===
class config:
    min_days = 3        # Minimum age of account. Default is 3.
    min_tweets = 30     # Minimum tweet count. Default is 30.
    min_followers = 3   # Minimum follower count. Default is 3.
    
    report_as_spam = True           # Report the user for spam. Default is 
                                    # True.
    block_if_following = False      # Block a follower if you follow them.
                                    # Default is False.
    unblock_when_blocked = False    # Unblock the user once you've blocked
                                    # them. Default is False.
    
    # OAuth fuckshit.
    # Get the OAuth keys from dev.twitter.com. Please set the permissions to
    # Read/Write. I think the variable names speak for themselves.
    oauth_consumerkey       = ''
    oauth_consumersecret    = ''
    oauth_accesstoken       = ''
    oauth_accesstokensecret = ''

# === CONFIG ENDS HERE, CODE STARTS HERE ===

import sys
import tweepy
import datetime
import traceback
try:
  import json
except ImportError:
  import simplejson as json

class autoblock:
    def __init__(self):
        self.active = True
        self.init_api()
        self.init_user_stream()
    
    def init_api(self):
        try:
            sys.stdout.write('-- Trying to log in... ')
            sys.stdout.flush()
            self.auth = tweepy.OAuthHandler(config.oauth_consumerkey, config.oauth_consumersecret)
            self.auth.set_access_token(config.oauth_accesstoken, config.oauth_accesstokensecret)
            
            tweepy.API.report_spam_2 = tweepy.binder.bind_api( # own report spam method because Tweepy's api.report_spam does not work
                path = '/users/report_spam.json',
                method = 'POST',
                payload_type = 'user',
                allowed_param = ['id', 'user_id', 'screen_name'],
                require_auth = True)
            
            self.api = tweepy.API(self.auth)
            self.me = self.api.me()
            sys.stdout.write('\r:: Logged in as ' + self.me.screen_name + ' ')
            sys.stdout.flush()
            
        except:
            sys.stdout.write('but I failed :-(\r!!\n')
            sys.stdout.flush()
            traceback.print_exc()
            sys.stdout.write('System halted.\n')
            sys.stdout.flush()
            exit(1)
        sys.stdout.write('\n')
        sys.stdout.flush()
    
    def init_user_stream(self):
        class StreamListener(tweepy.StreamListener):
            def on_data(self_, data):
                if '"event":"follow"' in data:
                    self.check_follower(json.loads(data)['source'])
                    
        ulistener = StreamListener()
        self.user_stream = tweepy.Stream(auth = self.auth, listener = ulistener)
    
    def run(self):
        if not self.user_stream.running:
            self.user_stream.userstream()
    
    def end(self):
        print 'Will now exit.'
        self.active = False
        self.user_stream.disconnect()
    
    def check_follower(self, data):
        if data['id'] == self.me.id: # We do not need to block ourselves.
            return
        to_block = False
        
        user = self.api.get_user(data['id'])
        
        following = user.following
        created_at = user.created_at 
        screen_name = user.screen_name
        tweet_count = user.statuses_count
        follower_count = user.followers_count
        
        days_difference = (datetime.datetime.now() - created_at).days
        
        print '-. New follower: ' + screen_name
        print ' | ' + screen_name + '\'s account was created: ' + str(created_at)
        print ' | ' + screen_name + ' has ' + str(tweet_count) + ' tweets'
        print ' | ' + screen_name + ' has ' + str(follower_count) + ' followers'
        if following:
            print ' | You are following ' + screen_name + "!"
        print ' `-.'
        if days_difference < config.min_days:
            print '   | Will be blocked because account is ' + str(days_difference) + ' days old.'
            to_block = True
        if tweet_count < config.min_tweets:
            print '   | Will be blocked because of less than ' + str(config.min_tweets) + ' tweets.'
            to_block = True
        if follower_count < config.min_followers:
            print '   | Will be blocked because of less than ' + str(config.min_followers) + ' followers.'
            to_block = True
        
        if following and (not config.block_if_following):
            print '   | Will NOT be blocked because you\'re following that account.'
            to_block = False
        
        if to_block:
            if config.report_as_spam:
                print '   `--- SPAMBLOCKING ' + screen_name + ' ---'
                self.api.report_spam_2(screen_name = user.screen_name)
            else:
                print '   `--- BLOCKING ' + screen_name + ' ---'
                self.api.create_block(screen_name = user.screen_name)
            if config.unblock_when_blocked:
                self.api.destroy_block(screen_name = user.screen_name)
        else:
            print '   `--- NOT BLOCKING ' + screen_name + ' ---'

def main():
  abb = autoblock()
  while abb.active:
    try:
      abb.run()
    except KeyboardInterrupt:
      abb.end()
    except:
      traceback.print_exc()

try:
    main()
except KeyboardInterrupt: 
    pass

# kate: indent-width 4; replace-tabs on; 