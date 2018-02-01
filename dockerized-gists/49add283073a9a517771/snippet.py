# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 12:24:41 2013

@author: cheesinglee
"""

import praw

from csv import DictWriter
from datetime import datetime
from time import gmtime
from bigml.api import BigML

SUBREDDITS = ['MachineLearning']
POST_KEYS = ['title','created_utc','score','subreddit','domain','is_self','over_18','selftext']
SCRAPE_AUTHORS = False

processed_users = {}

def get_author_info(a):
    if a:
        if a.id in processed_users:
            return processed_users[a.id]
        else:
            d = {}
            d['author_name'] = a.name
            d['author_over_18'] = a.over_18
            d['author_is_mod'] = a.is_mod
            d['author_is_gold'] = a.is_gold
            t = gmtime(a.created_utc)
            d['author_created_year_utc'] = t.tm_year
            d['author_created_mon_utc'] = t.tm_mon
            d['author_created_day_of_year_utc'] = t.tm_yday
            d['author_created_day_of_month_utc'] = t.tm_mday
            d['author_created_day_of_week_utc'] = t.tm_wday
            d['author_created_hour_utc'] = t.tm_hour
            d['author_created_min_utc'] = t.tm_min
            d['author_created_sec_utc'] = t.tm_sec
            processed_users[a.id] = d
            return d
    else:
        return {'author_name':'',
                'author_over_18':None,
                'author_is_mod':None,
                'author_is_gold':None,
                'author_created_year_utc':None,
                'author_created_mon_utc':None,
                'author_created_day_of_year_utc':None,
                'author_created_day_of_month_utc':None,
                'author_created_day_of_week_utc':None,
                'author_created_hour_utc':None,
                'author_created_min_utc':None,
                'author_created_sec_utc':None}

def process_post(post):
    d = {}
    postdict = vars(post)
    for key in POST_KEYS:
        val = postdict[key]
        try:
            val = val.lower()
        except:
            pass
        d[key] = val

    d['has_thumbnail'] = (post.thumbnail != u'default') and (post.thumbnail != u'self')

    post.replace_more_comments(limit=None,threshold=0)
    comments = post.comments
    flat_comments = praw.helpers.flatten_tree(comments)
    d['n_comments'] = len(list(flat_comments))

    if SCRAPE_AUTHORS:
        author_dict = get_author_info(post.author)
        for key,val in author_dict.iteritems():
            d[key] = val
    return d

def do_bigml(fname):
    api = BigML()
    src = api.create_source(fname)
    api.ok(src)
    api.create_dataset(src)
    dategen = {'field':'(epoch-fields (* 1000 (f "created_utc"))'}
    ds = api.create_dataset(src,args={'new_fields':[dategen]})
    api.ok(ds)


if __name__ == '__main__':
    r = praw.Reddit('Reddit Dataset builder')
    ids = []
    posts = []

    if len(SUBREDDITS) > 0:
        for subreddit in SUBREDDITS:
            print 'scraping subreddit:',subreddit
            sub = r.get_subreddit(subreddit)

            print 'scraping new posts...'
        #    posts =  [process_post(p) for p in sub.get_new(limit=1000)]
        #    ids = [p['id'] for p in posts]
            for post in sub.get_new(limit=1000):
                if post.id not in ids:
                    print post.title
                    posts.append(process_post(post))
                    ids.append(post.id)

            print 'scraping top posts...'
            for post in sub.get_top_from_all(limit=1000):
                if post.id not in ids:
                    print post.title
                    posts.append(process_post(post))
                    ids.append(post.id)

            print 'scraping controversial posts...'
            for post in sub.get_controversial_from_all(limit=1000):
                if post.id not in ids:
                    print post.title
                    posts.append(process_post(post))
                    ids.append(post.id)
    else:
        print 'scraping frontpage...'
        SUBREDDITS = ['frontpage']
        for post in r.get_front_page(limit=1000):
            print post.title
            posts.append(process_post(post))

    print 'scraped ',len(posts),' posts'
    filename = 'reddit_'+ '+'.join(SUBREDDITS) + '_' + datetime.now().isoformat() + '.csv'
    with open(filename,'w') as fid:
        csv_writer = DictWriter(fid,posts[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(posts)
    do_bigml(filename)
