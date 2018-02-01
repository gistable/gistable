#!/usr/bin/env python

'''
This code is adapted from the consensus best practice python Twitter feed 
consumer that's been floating around for a while now on StackOverflow etc. 
My only addition to speak of is TenminWriter. (A "tenmin" is ten minutes 
worth of stream. It's just a convenient chunk; you might want to make it 
shorter or longer.)

THERE ARE BUGS HERE. THIS IS BARELY TESTED. DO NOT TRUST IT.

To run it in this form you need:

- A developer account from Twitter (https://dev.twitter.com)

- An S3 bucket from Amazon, plus the s3cmd utility with its credentials 
  in .s3cfg or otherwise configured.

The result is an s3 bucket that gets a new file with the last 10 
minutes' tweets from a given area every 10 minutes. This works well to
run on an ec2 mini instance under tmux.

I've marked parts where you should fill in your own numbers/
credentials with CHANGEME.

Main todos:
- testing
- clarity-oriented cleanups
- *slowly* bring the backoff numbers back down (for long-term use)
- use boto

'''

import time
import pycurl
import urllib
import json
import oauth2 as oauth
import time
import bz2
from subprocess import call

class TenminWriter(object):
    def __init__(self):
        self.current = self.ts()
        self.outfile = self.new_file(self.current)
    def ts(self):
        return int(time.time()) / (60 * 10)
    def new_file(self, t):
        return bz2.BZ2File('%s.bz2' % t, 'w')
    def write(self, s):
        if self.ts() != self.current:
            self.update()
        self.outfile.write(s)
    def update(self):
        # This is pretty hacky. Should do more checks for common
        # problems, and not block on the shell calls.
        self.outfile.close()
        call(['s3cmd', 'put', '%s.bz2' % self.current, 's3://celoyd-twitter/']) # CHANGEME: s3 bucket name
        call(['rm', '%s.bz2' % self.current])
        self.current = self.ts()
        self.outfile = self.new_file(self.current)

writer = TenminWriter()

API_ENDPOINT_URL = 'https://stream.twitter.com/1.1/statuses/filter.json'
USER_AGENT = 'TweatStreem 1.0.0.0.0'

# CHANGEME: OAuth keys from Twitter
OAUTH_KEYS = {'consumer_key': 'xxx',
              'consumer_secret': 'yyy',
              'access_token_key': 'xxx',
              'access_token_secret': 'xyz'}
 
POST_PARAMS = {'include_entities': 0,
               'stall_warning': 'true',
               'locations': '38,32,120,56'} # CHANGEME: your own geo bounding box

class TwitterStream:
    def __init__(self):
        self.oauth_token = oauth.Token(key=OAUTH_KEYS['access_token_key'], secret=OAUTH_KEYS['access_token_secret'])
        self.oauth_consumer = oauth.Consumer(key=OAUTH_KEYS['consumer_key'], secret=OAUTH_KEYS['consumer_secret'])
        self.conn = None
        self.buffer = ''
        self.setup_connection()
 
    def setup_connection(self):
        if self.conn:
            self.conn.close()
            self.buffer = ''
        self.conn = pycurl.Curl()
        self.conn.setopt(pycurl.URL, API_ENDPOINT_URL)
        self.conn.setopt(pycurl.USERAGENT, USER_AGENT)

        self.conn.setopt(pycurl.ENCODING, 'deflate, gzip')
        self.conn.setopt(pycurl.POST, 1)
        self.conn.setopt(pycurl.POSTFIELDS, urllib.urlencode(POST_PARAMS))
        self.conn.setopt(pycurl.HTTPHEADER, ['Host: stream.twitter.com',
                                             'Authorization: %s' % self.get_oauth_header()])
        # self.handle_tweet is the method that are called when new tweets arrive
        self.conn.setopt(pycurl.WRITEFUNCTION, self.handle_tweet)

    def get_oauth_header(self):
        params = {'oauth_version': '1.0',
                  'oauth_nonce': oauth.generate_nonce(),
                  'oauth_timestamp': int(time.time())}
        req = oauth.Request(method='POST', parameters=params, url='%s?%s' % (API_ENDPOINT_URL, urllib.urlencode(POST_PARAMS)))
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), self.oauth_consumer, self.oauth_token)
        return req.to_header()['Authorization'].encode('utf-8')

    def start(self):
        backoff_network_error = 0.25
        backoff_http_error = 5
        backoff_rate_limit = 60
        while True:
            self.setup_connection()
            try:
                self.conn.perform()
            except:
                # Network error, use linear back off up to 16 seconds
                print 'Network error: %s' % self.conn.errstr()
                print 'Waiting %s seconds before trying again' % backoff_network_error
                time.sleep(backoff_network_error)
                backoff_network_error = min(backoff_network_error + 1, 16)
                continue
            # HTTP Error
            sc = self.conn.getinfo(pycurl.HTTP_CODE)
            if sc == 420:
                # Rate limit, use exponential back off starting with 1 minute and double each attempt
                print 'Rate limit, waiting %s seconds' % backoff_rate_limit
                time.sleep(backoff_rate_limit)
                backoff_rate_limit *= 2
            else:
                # HTTP error, use exponential back off up to 320 seconds
                print 'HTTP error %s, %s' % (sc, self.conn.errstr())
                print 'Waiting %s seconds' % backoff_http_error
                time.sleep(backoff_http_error)
                backoff_http_error = min(backoff_http_error * 2, 320)

    def handle_tweet(self, data):
        """ This method is called when data is received through Streaming endpoint.
        """
        self.buffer += data
        if data.endswith('\r\n'):
            #print self.buffer
            # complete message received
            message = json.loads(self.buffer.strip())
            if message.get('limit'):
                print 'Rate limiting caused us to miss %s tweets' % (message['limit'].get('track'))
            elif message.get('disconnect'):
                raise Exception('Got disconnect: %s' % message['disconnect'].get('reason'))
            elif message.get('warning'):
                print 'Got warning: %s' % message['warning'].get('message')
            else:
                writer.write(self.buffer)
            self.buffer = ''
                #print message #'Got tweet with text: %s' % message.get('text')


if __name__ == '__main__':
    ts = TwitterStream()
    ts.setup_connection()
    ts.start()