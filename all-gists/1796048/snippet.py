#!/usr/bin/env python

import sys
import urllib2
import json
from collections import defaultdict

from nltk import word_tokenize

IGNORED_WORDS = ["!", ".", ",", "(", ")", "'s", ":", "?", "...", "$", 
                 "<", ">", "''", "``", "-", "c", "'", "--", "&",
                 "and", "the", "or", "not", "i", "you", "to", "this", 
                 "of", "in", "for", "a", "an", "and", "your", "with", 
                 "me", "my", "be", "these", "that", "do", "at", "no", "so",
                 "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", 
                 "http", "@", "is", "am", "are", "it", "if", "n't", "'em",
                 "from", "one", "on", "up", "like", "we", "their", "they",
                 "'ll", "'d", "'m", "//www.youtube.com/watch", "by", "have",
                 "just", "will", "as"]

def get_json(url):
    """ Return the parsed JSON from a url. """
    print "GET %s" % url
    f = urllib2.urlopen(url)
    return json.loads(f.read())


def fb_feed_url(access_token):
    """ The graph api url for your facebook feed. access_token should be 
    a valid facebook access token as a string.
    """
    return "https://graph.facebook.com/me/home?access_token=%s" % access_token


def fb_news_feed(access_token):
    """ Returns a set number of pages from a facebook news feed as a 
    list of parsed json. 
    """
    feed_url = fb_feed_url(access_token)
    page_json = []
    
    for x in range(0, 100):
        json = get_json(feed_url)
        page_json.append(json)
        
        # Break if there's not enough data to continue
        if 'paging' in json and 'next' in json['paging']:
            feed_url = json['paging']['next']
        else:
            break
            
    return page_json


def word_count(words):
    """ Count the occurrences of each word. Words should be a list of strings
    that you might get from str.split() or nltk.word_tokenize().
    """
    seen = defaultdict(lambda: 0)
    
    for w in words:
        if w.lower() not in IGNORED_WORDS:
            seen[w] += 1
    
    return seen


def word_cloud_sizes(counts):
    max_count = max(counts.values())
    min_size, max_size = (1, 5)
    word_sizes = defaultdict(lambda : 1)
    
    for word in counts:
        if counts[word] > 1:
            size = int(float(counts[word]) * (max_size - 1) / max_count) + 1
            word_sizes[word] = size
    
    return word_sizes

def word_cloud_header():
    return """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
    <title>My Facebook Word Cloud</title>
    <style type=\"text/css\">
.size-1 { font-size: 10pt; }
.size-2 { font-size: 16pt; }
.size-3 { font-size: 28pt; }
.size-4 { font-size: 36pt; font-weight: bold; }
.size-5 { font-size: 48pt; font-weight: bold; }
.word-cloud { margin: 0 auto; width: 600px; padding-top: 10px; }
    </style>
</head>
<body>
<div class="word-cloud">
"""

def word_cloud_footer():
    return """
</div>
</body>
</html>
"""

def word_cloud_html(sizes):
    def word_html(word, size):
        return "<span class=\"size-%s\">%s</span>" % (size, word)

    return ' '.join([word_html(w, s) for w, s in sizes.items()])
    

if __name__ == "__main__":
    access_token = sys.argv[1]
    
    pages = fb_news_feed(access_token)
    messages = [post['message'] for page in pages 
                                    for post in page['data']
                                        if 'message' in post]
    comments = [comment['message'] for page in pages
                                    for post in page['data']
                                        if 'comments' in post and 'data' in post['comments']
                                            for comment in post['comments']['data']
                                                if 'if message' in comment]
    messages.extend(comments)
    
    tokens = [token for msg in messages for token in word_tokenize(msg)]
    counts = word_count(tokens)
    
    sizes = word_cloud_sizes(counts)
    
    print ''.join([
        word_cloud_header(),
        word_cloud_html(sizes),
        word_cloud_footer()])