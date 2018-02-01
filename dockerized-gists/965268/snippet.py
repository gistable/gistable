
import urllib2
import json
import sys
import os
import re
import time
import rfc822
import sqlite3
import datetime

db_file='sample_data.db'

def db_init():
    if not os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute('''create table item (id integer primary key, timestamp timestamp, query text, service text, item_id text unique, text text unique, sentiment text)''')
    else:
        conn = sqlite3.connect(db_file)
    return conn

def facebook_feed(query, last_ts = None, **kwargs):
    db = db_init()
    cursor = db.cursor()
    if not last_ts:
        try:
            cursor.execute('SELECT timestamp FROM item WHERE service=? AND query=? ORDER BY item_id DESC LIMIT 1',['facebook',query])
            last_ts = cursor.fetchone()[0]
        except:
            last_ts = None
    url = "https://graph.facebook.com/search?q=%s&type=post&limit=25&ince=%s" % (query,last_ts)
    try:
        data = json.loads(urllib2.urlopen(url).read())
    except Exception,e:
        data = None
        pass
    if data:
        items = data['data']
        if data.get('paging'):
            prev_url = data['paging']['previous']
        else:
            prev_url = url
        for item in items:
            if item.has_key('message'):
                text = item['message'].encode('utf8')
                item_id = item['id']
                time_format = "%Y-%m-%dT%H:%M:%S+0000"
                timestamp = datetime.datetime.strptime(item['created_time'], time_format)
                try:
                    print timestamp,query,'facebook',item_id,text
                    cursor.execute('INSERT INTO item VALUES (NULL,?,?,?,?,?,NULL)',[timestamp,query,u'facebook',item_id,text])
                    last_ts = timestamp
                except sqlite3.IntegrityError,e:
                    pass
    db.commit()
    db.close()
    return last_ts

def twitter_feed(query, last_id = None, **kwargs):
    db = db_init()
    cursor = db.cursor()
    if not last_id:
        try:
            cursor.execute('SELECT item_id FROM item WHERE service=? AND query=? ORDER BY item_id DESC LIMIT 1',['twitter',query])
            last_id = cursor.fetchone()[0]
        except:
            last_id = None
    url = "http://search.twitter.com/search.json?lang=en&q=%s&since_id=%s" % (query,last_id)
    try:
        data = json.loads(urllib2.urlopen(url).read())
    except Exception,e:
        data = None
        pass
    if data:
        items = data['results']
        for item in items:
            text = item['text'].encode('utf8')
            item_id = item['id']
            timestamp = datetime.datetime.fromtimestamp(rfc822.mktime_tz(rfc822.parsedate_tz(item['created_at'])))
            try:
                print timestamp,query,'twitter',item_id,text
                cursor.execute('INSERT INTO item VALUES (NULL,?,?,?,?,?,NULL)',[timestamp,query,u'twitter',item_id,text])
                last_id = item_id
            except sqlite3.IntegrityError,e:
                pass
    db.commit()
    db.close()
    return last_id

def collect(query):
    twitter_last_id = None
    facebook_last_ts = None
    while True:
        time.sleep(1)
        twitter_last_id = twitter_feed(query,twitter_last_id)
        facebook_last_ts = facebook_feed(query,facebook_last_ts)

# to run just do:
#collect('android')
