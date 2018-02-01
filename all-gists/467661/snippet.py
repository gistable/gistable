#!/usr/bin/env python 

# Watch and rank links coming from twitter's public timeline. 
# Currently this doesn't really work all that well, as we can only get 20 
# tweets a minute, but it's an idea.

# Requires the following non-standard python libs: (install with easy_install)
# * simplejson
# * functional
# * sqlalchemy

import urllib, simplejson as json, re, operator
import sqlalchemy as sql
from sqlalchemy import orm, ext
from sqlalchemy.ext import declarative
from functional import partial, flip

# helpers
def flatten(l):
    return reduce(operator.add, l)

def encode(str, *args):
    return str.encode(*args)

# DB stuff
Session = sql.orm.sessionmaker()
Base    = sql.ext.declarative.declarative_base()
class Tweet(Base):
    __tablename__ = 'tweets'
    tweet_id = sql.Column(sql.Integer, primary_key = True)
    def __init__(self, id):
        self.tweet_id = id

class Link(Base):
    __tablename__ = 'links'

    id      = sql.Column(sql.Integer, primary_key = True)
    url     = sql.Column(sql.String(500))
    count   = sql.Column(sql.Integer)

    def __init__(self, url, count):
        self.url = url
        self.count = count

    def __repr__(self):
        return "<Link %s (%d)>" % (self.url, self.count)

# create the table if it doesn't exist
engine = sql.create_engine('sqlite:///tweets.db')
Tweet.metadata.create_all(engine)
Link.metadata.create_all(engine)

# get the timeline and links in it
timeline = urllib.urlopen('http://www.twitter.com/statuses/public_timeline.json').read()
timeline = json.loads(timeline)

encode = partial(flip(encode), 'ascii')
find_urls = re.compile(r'http://[^\s]+[^\s\.]')

links = []
tweets  = [Tweet(t['id']) for t in timeline]
for matches in [map(encode, find_urls.findall(t['text'])) for t in timeline]:
    if len(matches) > 0:
        tweet_links = []
        for url in matches:
            # find the real URL (after redirects)
            url = urllib.urlopen(url)
            url = url.geturl()
            tweet_links.append(Link(url, 1))
        links.append(tweet_links)
    else:
        links.append(None)


stuff = zip(tweets, links)
stuff = filter(lambda s: s[1] != None, stuff)

# db stuff
Session.configure(bind = engine)
session = Session()

# if the tweet hasn't been seen before
for tweet, links in stuff:
    if session.query(Tweet).filter_by(tweet_id = tweet.tweet_id).count() == 0:
        session.add(tweet)
        for new_link in links:
            try:
                orig_link = session.query(Link).filter_by(url = new_link.url).one()
            except Exception:
                session.add(new_link)
            else:
                orig_link.count += 1
                session.add(orig_link)

# done adding, commit and close
session.commit()
session.close()