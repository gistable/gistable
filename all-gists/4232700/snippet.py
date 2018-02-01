#!/usr/bin/env python
# encoding: utf-8
"""
linkedin-1-oauth.py

Created by Thomas Cabrol on 2012-12-03.
Copyright (c) 2012 dataiku. All rights reserved.

Doing the oauth dance to get your LinkedIn token
This is taken from :
http://developer.linkedin.com/documents/authentication
"""

import oauth2 as oauth
import urlparse

consumer_key = "your-consumer-key-here"
consumer_secret = "your-consumer-secret-here"


class LinkedIn(object):
    
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        
    def request_token(self):
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(self.consumer)
        request_token_url      = 'https://api.linkedin.com/uas/oauth/requestToken?scope=r_network'
        resp, content = client.request(request_token_url, "POST")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])
        self.request_token = dict(urlparse.parse_qsl(content))
        print "Request Token:"
        print "    - oauth_token        = %s" % self.request_token['oauth_token']
        print "    - oauth_token_secret = %s" % self.request_token['oauth_token_secret']
        print
        
    def authorize(self):
        authorize_url =      'https://api.linkedin.com/uas/oauth/authorize'
        print "Go to the following link in your browser:"
        print "%s?oauth_token=%s" % (authorize_url, self.request_token['oauth_token'])
        print
        accepted = 'n'
        while accepted.lower() == 'n':
            accepted = raw_input('Have you authorized me? (y/n) ')
        self.oauth_verifier = raw_input('What is the PIN? ')
        
    def access(self):
        access_token_url = 'https://api.linkedin.com/uas/oauth/accessToken'
        token = oauth.Token(self.request_token['oauth_token'], self.request_token['oauth_token_secret'])
        token.set_verifier(self.oauth_verifier)
        client = oauth.Client(self.consumer, token)
        resp, content = client.request(access_token_url, "POST")
        self.access_token = dict(urlparse.parse_qsl(content))
        print "Access Token:"
        print "    - oauth_token        = %s" % self.access_token['oauth_token']
        print "    - oauth_token_secret = %s" % self.access_token['oauth_token_secret']
        print
        print "You may now access protected resources using the access tokens above."
        print 
        
    def dance(self):
        self.request_token()
        self.authorize()
        self.access()



if __name__ == '__main__':
	l = LinkedIn(consumer_key, consumer_secret)
	l.dance()
