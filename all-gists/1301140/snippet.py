# -*- coding: utf-8 -*-

import sys;reload(sys);sys.setdefaultencoding('utf-8')
import twitter
import time
import commands, itertools

consumer_key    = ...
consumer_secret = ...
access_key = ...
access_secret = ...

# Как получить ключи можно почитать в любом туториале по написанию приложений для твиттера.

class Twitter:
    def __init__(self):
        self.read_state()
        self.api =  twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret,
                        access_token_key=access_key, access_token_secret=access_secret,
                        input_encoding='utf-8')

    def read_state(self):
        try:
            with open('/var/tmp/speetter.state', 'r') as fl:
                (self.since_id, self.since_reply) = map(int, fl.read().split(','))
        except ValueError:
            print 'oooPs?'
            self.since_id, self.since_reply = None, None

    def write_state(self):
        with open('/var/tmp/speetter.state', 'w') as fl:
            fl.write('%d,%d' % (self.since_id, self.since_reply))

    def get_replies(self):
        r = self.api.GetMentions(since_id = self.since_reply)
        if not r:
            return []
        self.since_reply = max(r, key = lambda x: x.id).id
        return reversed(r)

    def get_timeline(self):
        r = self.api.GetFriendsTimeline(since_id = self.since_id, retweets=True)
        if not r:
            return []
        self.since_id = max(r, key = lambda x: x.id).id
        return reversed(r)

    def news(self, callback):
        for status in itertools.chain(self.get_replies(), self.get_timeline()):
            st = status.user.name.encode('utf-8') + " пишет " + status.text.encode('utf-8')
            callback(st)
        self.write_state()

def say(st):
    res = []
    for x in str(st).split(' '):
        if not x.startswith('http'):
            res.append(x)
        else:
            res.append(' (ссылка) ')
    st = ' '.join(res)
    st =st.replace('@bobuk', 'Бобук')\
        .replace(':)', '(улыбка)').replace(':-)', '(улыбка)')\
        .replace(':(', '(печаль)').replace(':-(', '(печаль)')
    print st
    commands.getoutput("say '%s'" % st)

t = Twitter()
while True:
    print 'refresh since ', t.since_id
    t.news(say)
    time.sleep(90)
