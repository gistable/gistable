#!/usr/bin/env python
# -*- coding: utf8 -*-

# Copyright (c) 2012, Valentin Lorentz
#
# Permission is hereby granted, free  of charge, to any person obtaining
# a  copy  of this  software  and  associated  documentation files  (the
# "Software"), to  deal in  the Software without  restriction, including
# without limitation  the rights to  use, copy, modify,  merge, publish,
# distribute,  sublicense, and/or sell  copies of  the Software,  and to
# permit persons to whom the Software  is furnished to do so, subject to
# the following conditions:
#
# The  above  copyright  notice  and  this permission  notice  shall  be
# included in all copies or substantial portions of the Software.
#
# THE  SOFTWARE IS  PROVIDED  "AS  IS", WITHOUT  WARRANTY  OF ANY  KIND,
# EXPRESS OR  IMPLIED, INCLUDING  BUT NOT LIMITED  TO THE  WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT  SHALL THE AUTHORS OR COPYRIGHT HOLDERS  BE LIABLE FOR ANY
# CLAIM, DAMAGES OR  OTHER LIABILITY, WHETHER IN AN  ACTION OF CONTRACT,
# TORT  OR OTHERWISE, ARISING  FROM, OUT  OF OR  IN CONNECTION  WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""The words 'crypter' and 'cryptage' do not exist in French.
However, many people use them, so it is our duty to tell them they
should not use them.

WARNING: One bot for the whole Twitter is enough. The source code is
here only as a tool for you building bots like this one, with other
triggers. Please DO NOT ABUSE of bots, they can be a pain.
The author is not responsible for the use made of this source code."""

import time
import json
from urllib import urlencode

import twitter
import requests

# Import the configuration. These variables should be strings.
# See Twitter documentation to generate them.
from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

# Informations for debugging purposes. DEBUG is a boolean and OWNER is
# a string. If DEBUG is True, the bot will only response to tweets
# from the OWNER.
from config import DEBUG, OWNER

# Words that trigger the bot
BLACKLIST = (u'cryptage', u'crypté', u'crypter', u'cryptés', u'cryptation')

# Words that prevent the bot from replying (possibly someone else telling that
# a word does not exist.
WHITELIST = (u'existe', u'bot', u'chiffrer', u'chiffré', u'chiffrés',
u'chiffrement', u'chiffrage',u'dictionnaire', u'¿', u'magic crypter'
u'este crypter', u'traduct', u'sic', u'FUD', u'fud', u'dis', u'dire', u'pas')

# The template used for noticing the user that he uses a word which does
# not exist.
# Should contain one of the word of the WHITELIST, if you do not want the bot
# to enter an infinite loop.
NOTICE_TEMPLATE = (u'@%(user)s Le mot « %(word)s » n\'existe pas '
                u'en Français. http://ur1.ca/87cu7')

class Bot(object):
    def __init__(self):
        self._api = twitter.Api(
                consumer_key=CONSUMER_KEY,
                consumer_secret=CONSUMER_SECRET,
                access_token_key=ACCESS_KEY,
                access_token_secret=ACCESS_SECRET)
        self._max_id = {} # Max ID found for each keyword

    def search(self, keyword):
        """Return all new messages containing the keyword."""
        payload = {'q': keyword.encode('ascii', 'replace')}
        first_query = (keyword not in self._max_id)
        if not first_query:
            # Don't fetch messages we already processed.
            payload.update({'since_id': self._max_id[keyword]})
        url = 'http://search.twitter.com/search.json?%s' % urlencode(payload)
        try:
            r = requests.get(url)
        except KeyboardInterrupt as e:
            raise e
        except:
            print 'max query exceeded'
            self._max_id[keyword] += 1
            return []
        if r.status_code != requests.codes.ok:
            print 'warning: %i:%s' % (r.status_code, r.content)
            return []

        result = json.loads(r.content)
        self._max_id.update({keyword: result['max_id']})
        results = [x for x in result['results']
                if (u' %s ' % keyword) in x['text']]
        if first_query:
            return []
        elif DEBUG:
            # Return only tweets from the owner. This avoids spamming while
            # debugging.
            return [x for x in results if x['from_user'] == OWNER]
        else:
            return results

    def run(self):
        """Main loop for the bot."""
        try:
            self._daemon()
        except KeyboardInterrupt:
            # Prevent traceback
            pass

    def _daemon(self):
        while True:
            for word in BLACKLIST:
                tweets = self.search(word)
                if tweets != []:
                    print tweets
                for tweet in tweets:
                    if self.should_reply(tweet):
                        self.notice(word, tweet['from_user'], tweet['id'])
            time.sleep(5 if DEBUG else 120)

    def should_reply(self, tweet):
        """Return whether we should reply to this tweet or not."""
        for word in WHITELIST:
            if word.lower() in tweet['text'].lower():
                return False
        # TODO: Check whether the user asked to stop noticing him.
        return True

    def notice(self, word, user, id_=None):
        """Notice the user that the word does not exist."""
        print 'Sending notice to %s about %s.' % (user, word)
        try:
            self._api.PostUpdate(NOTICE_TEMPLATE % {'user': user, 'word': word},
                    in_reply_to_status_id=id_)
        except:
            print 'failed.'


if __name__ == '__main__':
    try:
        Bot().run()
        print 'foo'
    except KeyboardInterrupt:
        pass
    print 'Exiting.'
