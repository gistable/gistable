#!/usr/bin/python -u
#
# Usage: ./trace.py <tweetId>
#

import sys
import tweepy
import Queue
import time
import json
import redis

CONSUMER_KEY = 'xxx'
CONSUMER_SECRET = 'xxx'
ACCESS_KEY = 'xxx'
ACCESS_SECRET = 'xxx'
REDIS_FOLLOWERS_KEY = "followers:%s"

# Retweeter who have not yet been connected to the social graph
unconnected = {}
# Retweeters connected to the social graph...become seeds for deeper search
connected = Queue.Queue()
# Social graph
links = []
nodes = []


#----------------------------------------
def addUserToSocialGraph (parent, child):
# parent: tweepy.models.User
# child:  tweepy.models.User
#----------------------------------------
    global links;

    
    if (child):
        nodes.append ({'id':child.id,
                       'screen_name':child.screen_name,
                       'followers_count':child.followers_count,
                       'profile_image_url':child.profile_image_url})

        # TODO: Find child and parent indices in nodes in order to create the links
        if (parent):
            print (nodes)
            print ("Adding to socialgraph: %s ==> %s" % (parent.screen_name, child.screen_name))
            links.append ({'source':getNodeIndex (parent), 
                           'target':getNodeIndex (child)})


#----------------------------------------
def getNodeIndex (user):
# node: tweepy.models.User
#----------------------------------------
    global nodes
    for i in range(len(nodes)):
        if (user.id == nodes[i]["id"]):
            return i

    return -1


#----------------------------------------
def isFollower (parent, child):
# parent: tweepy.models.User
# child:  tweepy.models.User
#----------------------------------------
    global red
    
    # Fetch data from Twitter if we dont have it
    key = REDIS_FOLLOWERS_KEY % parent.screen_name
    if ( not red.exists (key) ):
        print ("No follower data for user %s" % parent.screen_name)
        crawlFollowers (parent)

    cache_count = red.hlen (key)
    if ( parent.followers_count > (cache_count*1.1) ):
        print ("Incomplete follower data for user %s. Have %d followers but should have %d (exceeds 10% margin for error)." 
               % (parent.screen_name, cache_count, parent.followers_count))
        crawlFollowers (parent)
    
    return red.hexists (key, child.screen_name)


#----------------------------------------
def crawlFollowers (user):
# user: tweepy.models.User
#----------------------------------------
    print ("Retrieving followers for %s (%d)" % (user.screen_name, user.followers_count))
    count = 0
    follower_cursors = tweepy.Cursor (api.followers, id = user.id)
    followers_iter = follower_cursors.items()
    follower = None
    while True:
        try:
            # We may have to retry a failed follower lookup
            if ( follower is None ):
                follower = followers_iter.next()

                # Add link to Redis
                red.hset ("followers:%s" % user.screen_name, follower.screen_name, follower.followers_count)

                follower = None
                count += 1
                
        except StopIteration:
            break
        except tweepy.error.TweepError as (err):
            print ("Caught TweepError: %s" % (err))
            if (err.reason == "Not authorized" ):
                print ("Not authorized to see users followers. Skipping.")
                break
            limit = api.rate_limit_status()
            if (limit['remaining_hits'] == 0):
                seconds_until_reset = int (limit['reset_time_in_seconds'] - time.time())
                print ("API request limit reached. Sleeping for %s seconds" % seconds_until_reset)
                time.sleep (seconds_until_reset + 5)
            else:
                print ("Sleeping a few seconds and then retrying")
                time.sleep (5)

    print ("Added %d followers of user %s" % (count, user.screen_name))


#----------------------------------------
# Main
#----------------------------------------
tweetId =  sys.argv[1]

# Connect to Redis
red = redis.Redis(unix_socket_path="/tmp/redis.sock")

# Connect to Twitter
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)
print (api.rate_limit_status())

# Get original Tweet details
status = api.get_status (tweetId)
connected.put(status.user)
addUserToSocialGraph (None, status.user)
retweets = api.retweets (status.id)
print ("Tweet %s, originally posted by %s, was retweeted by..." % (status.id, status.user.screen_name))
for retweet in retweets:
    print (retweet.user.screen_name)
    unconnected[retweet.user.screen_name] = retweet.user;

# Pivot
while not (connected.empty() or len(unconnected)==0):
    # Get next user 
    pivot = connected.get()

    # Check followers of this user against unconnected retweeters
    print ("Looking through followers of %s" % pivot.screen_name)
    for (screen_name, retweeter) in unconnected.items():
        if (isFollower(pivot, retweeter)):
            print ("%s <=== %s" % (pivot.screen_name, retweeter.screen_name))
            connected.put (retweeter)
            addUserToSocialGraph (pivot, retweeter)
            del unconnected[retweeter.screen_name]
        else:
            print ("%s <=X= %s" % (pivot.screen_name, retweeter.screen_name))
                

# Add unconnected nodes to social graph
for (screen_name, user) in unconnected.items():
    addUserToSocialGraph (None, user)
                
# Encode data as JSON
filename = "%s.json" % status.id
print ("\n\nWriting JSON to %s" % filename)
tweet = {'id':status.id,
         'retweet_count':status.retweet_count,
         'text':status.text,
         'author':status.user.id}
         
f = open (filename, 'w')
f.write (json.dumps({'tweet':tweet, 'nodes':nodes, 'links':links}, indent=2))
f.close

sys.exit()