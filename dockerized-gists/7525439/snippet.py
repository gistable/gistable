# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from urllib2 import urlopen
import json



def download_hn_page(page_id=None):
    # HN unofficial API: http://api.ihackernews.com/
    url = 'http://api.ihackernews.com/page' + ('/%s' % page_id if page_id else '')
    u = urlopen(url)
    
    items = json.load(u)['items']
    for item in items:
        yield item['title']

# <codecell>

import string

def get_words():
    punct = set(string.punctuation)
    
    for item in download_hn_page():
        for word in item.split():
            yield ''.join(c for c in word if c not in punct)

# <codecell>

def build_words_dict():
    punct = set(string.punctuation)

    d = {}
    prev_word = None

    for item in download_hn_page():
        
        for word in item.split():
            w = ''.join(c for c in word if c not in punct)
            d.setdefault(prev_word, []).append(w)
            prev_word = w

        prev_word = None
        
    return d

# <codecell>

import random

def get_next_word(words_dict, prev_word):
    d = words_dict.get(prev_word)
    return random.choice(d) if d else None
    
def build_twit(words_dict, min_words=3, max_words=7, stop_chance=0.4):
    w = ''
    prev_word = None
    len_words = 0

    while len(w) < 140 and len_words < max_words:
        cur_word = get_next_word(words_dict, prev_word)
        w += ' %s' % cur_word
        len_words += 1
        
        if len_words > min_words:
            if random.random() <= stop_chance:
                break
        
        prev_word = cur_word
        

    return w.strip().title()

# <codecell>

from twitter import *

def auth_twitter():

    return Twitter(auth=OAuth(otoken, osecret, ckey, csecret))

# <codecell>

random.seed()
msg = build_twit(build_words_dict())

t = auth_twitter()

print msg
t.statuses.update(status=msg)

