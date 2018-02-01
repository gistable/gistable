from twitter import Twitter, OAuth, TwitterHTTPError


OAUTH_TOKEN = 'foo'
OAUTH_SECRET = 'bar'
CONSUMER_KEY = 'baz'
CONSUMER_SECRET = 'bat'

t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))


def search_tweets(q, count=100, max_id=None):
    return t.search.tweets(q=q, result_type='recent', count=count, lang="en", max_id=max_id)


def favorites_create(tweet):
    try:
        result = t.favorites.create(_id=tweet['id'])
        print "Favorited: %s, %s" % (result['text'], result['id'])
        return result
    except TwitterHTTPError as e:
        print "Error: ", e
        return None


def search_and_fav(q, count=100, max_id=None):
    result = search_tweets(q, count, max_id)
    first_id = result['statuses'][0]['id']
    last_id = result['statuses'][-1]['id']
    success = 0
    for t in result['statuses']:
        if favorites_create(t) is not None:
            success += 1

    print "Favorited total: %i of %i" % (success, len(result['statuses']))
    print "First id %s last id %s" % (first_id, last_id)
