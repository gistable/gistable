#!/usr/bin/env python
# This is a simple Twitter bot which listens to a track stream for a comma delimited
# list of terms/tags (PRIMARY_TRACK_LIST).  From this stream, it will retweet any 
# tweet that matches the secondary regex (SECONDARY_REGEX_FILTER).
#
# This example is a #Haiti & #Chile Twitter stream listener for TweakTheTweet syntax.
#
# Requires Python 2.6
# Requires Tweepy http://github.com/joshthecoder/tweepy
#
# (cc) http://creativecommons.org/licenses/by-nc-sa/3.0/us/
# Based on: http://github.com/joshthecoder/tweepy-examples
# Modifications by @ayman

import time
from getpass import getpass
from textwrap import TextWrapper
import tweepy
import re

# Primary Filter, can be a comma seperated list.
PRIMARY_TRACK_LIST = "#haiti,#chile"

# Secondary filter, must be a regex.
SECONDARY_REGEX_FILTER = "^.*(#need|#offer|#have|#closed|#open).*$"

class StreamWatcherListener(tweepy.StreamListener):
    status_wrapper = TextWrapper(width=70,
                                 initial_indent='  ',
                                 subsequent_indent='    ')
    prog = re.compile(SECONDARY_REGEX_FILTER,
                      re.IGNORECASE)

    def __init__(self, u, p):
        self.auth = tweepy.BasicAuthHandler(username = u,
                                            password = p)
        self.api = tweepy.API(auth_handler = self.auth,
                              secure=True,
                              retry_count=3)
        return

    def on_status(self, status):
        try:
            if self.prog.match(status.text):
                print "YES - Retweet"
                self.api.retweet(id = status.id)
            else:
                print "NO - pass on this one"
            print self.status_wrapper.fill(status.text)
            print '%s  %s via %s #%s\n' % (status.author.screen_name,
                                           status.created_at,
                                           status.source,
                                           status.id)
        except:
            # Catch any unicode errors while printing to console and
            # just ignore them to avoid breaking application.
            pass
        return

    def on_limit(self, track):
        print 'Limit hit! Track = %s' % track
        return

    def on_error(self, status_code):
        print 'An error has occured! Status code = %s' % status_code
        return True  # keep stream alive

    def on_timeout(self):
        print 'Timeout: Snoozing Zzzzzz'
        return

def main():
    username = raw_input('Twitter username: ')
    password = getpass('Twitter password: ')
    listener = StreamWatcherListener(username, password)
    stream = tweepy.Stream(username,
                           password,
                           listener,
                           timeout = None)
    track_list = [k for k in PRIMARY_TRACK_LIST.split(',')]
    stream.filter(track = track_list)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print '\nCiao!'
