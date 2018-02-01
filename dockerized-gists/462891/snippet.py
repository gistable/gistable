#/usr/bin/python
#-*- encoding:utf-8 -*-

#====== options =============
#Oauth用認証トークン  各自取得
ckey = ""
csecret = ""
atoken =""
atoken_secret = ""
#============================

import simplejson
import sqlite3,re
import random
import urllib, urllib2
import hmac, hashlib
import cgi
import time


reqt_url = 'http://twitter.com/oauth/request_token'
auth_url = 'http://twitter.com/oauth/authorize'
acct_url = 'http://twitter.com/oauth/access_token'
post_url = 'http://twitter.com/statuses/update.xml'
chirp_url ='http://chirpstream.twitter.com/2b/user.json' 

def make_signature(params, url, method, csecret, secret = ""):
    # Generate Signature Base String
    plist = []
    for i in sorted(params):
        plist.append("%s=%s" % (i, params[i]))

    pstr = "&".join(plist)
    msg = "%s&%s&%s" % (method, urllib.quote(url, ""),
                        urllib.quote(pstr, ""))

    # Calculate Signature
    h = hmac.new("%s&%s" % (csecret, secret), msg, hashlib.sha1)
    sig = h.digest().encode("base64").strip()
    
    return sig

def init_params():
    p = {
        "oauth_consumer_key": ckey,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": str(random.getrandbits(64)),
        "oauth_version": "1.0"
        }

    return p

def oauth_header(params):
    plist = []
    for p in params:
        plist.append('%s="%s"' % (p, urllib.quote(params[p])))
        
    return "OAuth %s" % (", ".join(plist))
    
def update(post):
    params = init_params()
    params["oauth_token"] = atoken
    params["status"] = urllib.quote(post, "")
    
    sig = make_signature(params, post_url, "POST", csecret, atoken_secret)
    params["oauth_signature"] = sig
    
    del params["status"]
    
    req = urllib2.Request(post_url)
    req.add_data("status=%s" % urllib.quote(post, ""))
    req.add_header("Authorization", oauth_header(params))
    
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError, e:
        print "Error: %s" % e
        print e.read()
        
def get_timeline():
    url = 'http://twitter.com/statuses/home_timeline.json'
    return __request(url)
    
def get_list(user):
    url ="http://api.twitter.com/1/%s/lists.json" % user
    return __request(url)

def __request(url,add_params={}):
    params = init_params()
    params["oauth_token"] = atoken
    
    params.update(add_params)
    
    sig = make_signature(params,url, "GET", csecret, atoken_secret)
    params["oauth_signature"] = sig
    
    req = urllib2.Request(url)
    req.add_header("Authorization", oauth_header(params))
    res = urllib2.urlopen(req)
    return simplejson.loads(res.read())
    
def get_chirp_stream():
    url ='http://chirpstream.twitter.com/2b/user.json' 
    params = init_params()
    params["oauth_token"] = atoken
    
    sig = make_signature(params, url, "GET", csecret, atoken_secret)
    params["oauth_signature"] = sig

    req = urllib2.Request(url)
    req.add_header("Authorization", oauth_header(params))
    return urllib2.urlopen(req)
    
def main():
    stream = get_chirp_stream()
    stream.readline()
    stream.readline()

    while 1:
            recv = stream.readline()
            json = simplejson.loads(recv)
            text = ""
            if json.has_key("event"):
                text = json["source"]["screen_name"]+ " "+ json["event"] +" "+json["target"]["screen_name"]

                if json["event"] in ("favorite","retweet"):
                    text+= "\t"+json["target_object"]["text"]
                    
            elif json.has_key("delete"):
                text = "delete:" + str(json["delete"]["status"]["user_id"]) +" "+ str(json["delete"]["status"]["id"])

            elif json.has_key("text"):
                text = "tweet:" + json["user"]["screen_name"] +" "+ json["text"]
                
            if text :
                print text

if __name__ == "__main__":
    main()
