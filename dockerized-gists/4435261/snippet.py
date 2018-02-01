""" 1) Download python twitter library from https://github.com/sixohsix/twitter
    2) Go to dev.twitter.com creaate an application and genenrate tokens
    3) Setup your tokens below
    4) python cleanup.py and your tweets are gone!
"""

from twitter import *

t = Twitter(
        auth=OAuth('--your-access-token-here',
            '--your-access-token-secret--here',
            '--your-consumer-key-here',
            '--your-consumer-key-secret-here')
        )
        
tweet_ids = []
screen_name = '--your-twitter-screename-here'

def get_tweets():
    print 'getting tweets...'
    tweets = t.statuses.user_timeline(screen_name=screen_name, count=200)
    for tweet in tweets:
        tweet_ids.append(tweet['id'])
    return True

def delete_tweets():
    print 'deleting tweets...'
    if len(tweet_ids) > 0:
        for id in tweet_ids:
            print id
            try:
                resp = t.statuses.destroy(id=id)
            except:
                pass
            del tweet_ids[tweet_ids.index(id)]
        return True
    else:
        return False

busy = True
while True and busy:
   busy = get_tweets() and delete_tweets()
   if not busy:
       t.statuses.update(status="Deleting...done. - https://gist.github.com/4435261")
       print "Done."