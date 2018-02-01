# twitterfavlinks.py - Throw back all your favorites that contain a url. Get any applicable redirects. Note there are Twitter API
# limits, so if you have a gazillion favorites, you probably won't get them all. YMMV
# 
# Author: @curi0usJack
#
# Dependencies:
#   Tweepy: sudo pip install tweepy
#   Twitter API access. Set up here: https://apps.twitter.com/

import tweepy
import urllib2
import re

# Enter the handle to search for (minus the @ sign). You can search for any user.
handle="HANDLETOSEARCHFOR"

# Enter twitter application keys
consumer_key = "CONSUMERKEY"
consumer_secret = "CONSUMERSECRET"
access_token = "ACCESSTOKEN"
access_secret = "ACCESSSECRET"

# Authenticate
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

favs = api.favorites(screen_name=handle, count=200)
f = open('twitterfavs.log', 'w')

# Get favorites
while len(favs) > 0:
    lastfavid = 0
    for fav in favs:
        toprint = False
        lastfavid = fav.id
        if handle not in fav.text:
            urls = re.findall("https:\/\/t\.co\/[a-zA-Z0-9]+", fav.text)
            strtxt = unicode(fav.text)
            fromuser = unicode(fav.user.screen_name)
            links = ""
            for url in urls:
                try:
                    landingurl = urllib2.urlopen(url).geturl()
                except:
                    landingurl = "(ERROR GETTING URL: {0})".format(url)

                strtxt = unicode(strtxt.replace(url, landingurl))
                strtxt = "@%s - %s" % (fromuser, strtxt)
                toprint = True

            if toprint:
                f.write(strtxt.replace('\n', ' ').encode('utf-8'))
                f.write('\n')
                f.flush()
                print strtxt.replace('\n', ' ')
                lastfavid = fav.id

    favs = api.favorites(screen_name=handle, count=200, max_id=lastfavid)

f.close()