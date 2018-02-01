#!/usr/bin/env python
#-*- coding:utf-8 -*-

from tweepy.streaming import StreamListener, Stream
from tweepy.auth import BasicAuthHandler
from tweepy.api import API
import tweepy
 
class MyStreamListener(StreamListener):
    def __init__(self, api=None):
        StreamListener.__init__(self, api=api)
 
    def on_status(self, status):
        print "@%s: %s" % (status.user.screen_name, status.text)
 
    def on_error(self, status_code):
        print "ERROR: ",status_code
 
    def on_limit(self, track):
        print "LIMIT: ", track
 
    def on_timeout(self):
        print "TIMEOUT!"

def filter_track():
    track=["python"]
    stream_auth = BasicAuthHandler('<USERNAME>', '<PASSWORD>')
    api = API()
    stream = Stream(stream_auth, MyStreamListener(api))
 
    print 'start filter track ', ','.join(track)
    stream.filter(track=track)

if __name__ == "__main__":
    filter_track()
 